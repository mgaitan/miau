#!/usr/bin/env python
"""
Miau: Remix speeches for fun and profit

Usage:
  miau -i <pattern>... -r <remix> [-o <output>] [-d <dump>] [--debug]
  miau -h | --help
  miau --version

Options:
  -i --input <pattern>          Input files (clip/s and its transcript/subtitle)
  -r --remix <remix>            Script text (txt or json)
  -d --dump <json>              Dump remix json. Can be loaded with -r to reuse aligment.
  -o --output <output>          Output filename
  -h --help                     Show this screen.
  --version                     Show version.
  --verbosity=<verbosity>       Set verbosity

"""

import os
import re
from itertools import chain
import glob
from collections import OrderedDict
import json
import tempfile
import logging
from aeneas.executetask import ExecuteTask
from aeneas.task import Task
from aeneas.tools.execute_task import ExecuteTaskCLI
from moviepy.editor import (
    VideoFileClip, AudioFileClip,
    concatenate_videoclips, concatenate_audioclips
)
from moviepy.tools import extensions_dict
from docopt import docopt, DocoptExit

VERSION = '0.1'

OFFSET_PATTERN = re.compile('^(?P<offset_begin>(\+|\-)+)?(?P<line>.*?)(?P<offset_end>(\+|\-)+)?$')

logging.basicConfig(format='[miau] %(asctime)s %(levelname)s: %(message)s',
                    level=10,
                    datefmt='%Y-%m-%d %H:%M:%S')


def fragmenter(source, remix_lines, debug=False):
    """return as many versions of the source text
    to ensure each line of the remix appears as an independent line
    at least once
    """

    for line in remix_lines:
        if line not in source:
            logging.exception('"%s" not found in the transcript', line)
            raise ValueError()

    def iterate(lines):

        current = source
        not_found = []
        for line in lines:
            if line not in current:
                not_found.append(line)
                continue
            current = current.replace(line, '\n{}\n'.format(line))
        current = current.replace('\n ', '\n').replace('\n\n', '\n')
        return current, not_found

    results = []
    count = 1
    while True:
        logging.info('Fragmenting source. Iteration %s', count)
        result, not_found = iterate(remix_lines)
        if debug:
            with open('_debug_source_{}.txt'.format(count), 'w') as _t:
                _t.write(result)
        count += 1
        results.append(result)
        if not not_found:
            # finish, as all remix lines were found
            break
        remix_lines = not_found

    return results


def fine_tuning(raw_line, offset_step=0.05):
    """given raw line potentially having symbols + or -
    at the beginning or the end. each symbol is equivalent to
    an ``offset_step`` (in seconds), positive or negative, which are applied
    to the segment cut then

    return  of the cleaned line, start_offset, end_offset

    >>> fine_tuning('++this is a line---'):
    {'this is a line': {'start_offset': 0.1, 'end_offset': -0.15}}
    """
    def _offset(symbols):
        if not symbols:
            return 0
        sign = int('{}1'.format(symbols[0]))
        return len(symbols) * offset_step * sign

    result = re.match(OFFSET_PATTERN, raw_line).groupdict()
    line = result.pop('line').strip()
    return {line: {k: _offset(v) for k, v in result.items()}}


def make_remix(remix_data, clips, output_type):
    """
    given a list in the form
    [('line 1': (start, end)), ('line 2': (start, end)) ...]

    return the moviepy clip resulting of concatenate each fragment
    """
    concatenate = (
        concatenate_videoclips if output_type == 'video' else concatenate_audioclips
    )
    clip = clips[0]
    return concatenate([clip.subclip(*segment) for line, segment in remix_data])


def get_fragments_database(clips, transcripts, remix_lines, debug=False, language='es'):
    """
    :parameter clips: list of input clips
    :parameter transcripts: raw texts of transcripts. map one-one to clips
    :remix_lines: list of remix lines dictionaries as returned by :func:`fine_tuning`

    """
    transcript = open(transcripts[0]).read().replace('\n', ' ').replace('  ', ' ')

    sources = fragmenter(transcript, remix_lines.keys(), debug=debug)
    # create Task object

    config_string = u"task_language={}|is_text_type=plain|os_task_file_format=json".format(language)
    fragments = OrderedDict()
    l_sources = len(sources)
    for i, source in enumerate(sources, 1):
        with tempfile.NamedTemporaryFile('w', delete=False) as f_in:
            f_in.write(source)
        output_json = '{}.json'.format(f_in.name)
        logging.info('Forcing aligment (step %s/%s)', i, l_sources)
        ExecuteTaskCLI(use_sys=False).run(arguments=[
            None,
            os.path.abspath(clips[0]),
            f_in.name,
            config_string,
            output_json
        ])
        output = json.load(open(output_json))
        for f in output['fragments']:
            line = f['lines'][0]
            try:
                offset_begin = remix_lines[line]['offset_begin']
                offset_end = remix_lines[line]['offset_end']
            except KeyError:
                offset_begin = 0
                offset_end = 0

            fragments.update({
                line: (
                    float(f['begin']) + offset_begin,
                    float(f['end']) + offset_end
                )
            })
    return fragments

def ensure_audio(clip):
    if isinstance(clip, AudioFileClip):
        return clip
    elif isinstance(clip, VideoFileClip):
        return clip.audio


def miau(clips, transcripts, remix, output_file=None, dump=None, debug=False, **kwargs):
    # TODO: allow multiples transcript/videos
    if not output_file:
        output_file = '{}.mp4'.format(os.path.basename(remix).rsplit('.')[0])

    mvp_clips = []

    for clip in clips:
        try:
            clip = VideoFileClip(clip)
        except KeyError:
            clip = AudioFileClip(clip)
        mvp_clips.append(clip)

    output_type = extensions_dict[os.path.basename(output_file).rsplit('.')[1]]['type']
    if output_type == 'video' and not all(isinstance(clip, VideoFileClip) for clip in mvp_clips):
        logging.error("Output expect to be a video but input clips aren't all videos")
        return
    elif output_type == 'audio':
        mvp_clips = [ensure_audio(clip) for clip in mvp_clips]

    with open(remix) as remix_fh:
        try:
            remix_data = json.load(remix_fh)
        except json.JSONDecodeError:
            remix_fh.seek(0)
            remix_lines = OrderedDict()
            for l in remix_fh:
                if not l.strip():
                    continue
                remix_lines.update(fine_tuning(l))
            fragments = get_fragments_database(clips, transcripts, remix_lines)
            remix_data = [(l, fragments[l]) for l in remix_lines]

    if dump:
        logging.info('Dumping remix data in %s', dump)
        json.dump(remix_data, open(dump, 'w'), indent=2)

    output_clip = make_remix(remix_data, mvp_clips, output_type)
    method = 'write_videofile' if output_type == 'video' else 'write_audiofile'
    logging.info('Creating output file')
    getattr(output_clip, method)(output_file)


def main(args=None):
    args = docopt(__doc__, argv=args, version=VERSION)
    if args['--debug']:
        logging.debug(args)

    media = []
    transcripts = []
    for f in chain.from_iterable(glob.iglob(pattern) for pattern in args['--input']):
        if f[-3:] in extensions_dict:
            media.append(f)
        else:
            transcripts.append(f)

    media_str = '   \n'.join(media)
    transcripts_str = '   \n'.join(transcripts)
    info = "Audio/Video:\n   {}\nTranscripts/subtitle:\n   {}".format(media_str, transcripts_str)

    if not media or len(media) != len(transcripts):
        raise DocoptExit(
            "Input mismatch: the quantity of video/audio and transcription/subtitles differs\n{}".format(info)
        )

    logging.info(info)

    return miau(
        media,
        transcripts,
        args['--remix'],
        args['--output'],
        args['--dump'],
        args['--debug']
    )


if __name__ == '__main__':
    main()