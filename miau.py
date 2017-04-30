#!/usr/bin/env python
"""
Miau: Remix speeches for fun and profit

Usage:

  miau -i <pattern>... -r <remix> [-o <output>] [-d <dump>] [--lang <lang>] [--debug]
  miau -h | --help
  miau --version

Options:
  -i --input <pattern>      Input files (clip/s and its transcripts)
  -r --remix <remix>        Script text (txt or json)
  -d --dump <json>          Dump remix as json.
                            Can be loaded with -r to reuse the aligment.
  -o --output <output>      Output filename
  -h --help                 Show this screen.
  --lang <lang>             Forced language (2-letter code) for inputs (default auto)
  --version                 Show version.
"""

from collections import OrderedDict
import glob
from itertools import chain
import json
import logging
import os
import re
import tempfile

from aeneas.tools.execute_task import ExecuteTaskCLI
from docopt import docopt, DocoptExit
import langdetect
from moviepy.editor import (
    VideoFileClip, AudioFileClip,
    concatenate_videoclips, concatenate_audioclips
)
from moviepy.tools import extensions_dict


VERSION = '0.1'

OFFSET_PATTERN = re.compile('^(?P<offset_begin>(\+|\-)+)?(?P<line>.*?)(?P<offset_end>(\+|\-)+)?$')

logging.basicConfig(format='[miau] %(asctime)s %(levelname)s: %(message)s',
                    level=10,
                    datefmt='%Y-%m-%d %H:%M:%S')


def fragmenter(source, remix_lines, debug=False):
    """
    return as many versions of the source text
    wrapped to ensure each remix verse (that exist on the source)
    appears as an independent line at least once as an
    independent line (if it exists)

    >>> fragmenter('I have a dream that one day this nation will rise up '
            'and live out the true meaning of its creed',
        ['I have a dream',
         'out the true',            # this two lines fit in the first iteration
         'the true meaning',        # but this requires a new one due repeat a part of verse
         'that all men are created equal'] # and this one is returned as not found.
         )
    (['\nI have a dream\nthat one day this nation will rise up and live \nout the true\nmeaning of its creed',
      'I have a dream that one day this nation will rise up and live out \nthe true meaning\nof its creed'],
     ['that all men are created equal'])


    """

    # fragments not present in this source.
    not_found_on_source = []
    for line in remix_lines:
        if line not in source:
            not_found_on_source.append(line)

    def iterate(lines):

        current = source
        not_found = []
        for line in lines:
            if line in not_found_on_source:
                continue

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

    return results, not_found_on_source


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


def make_remix(remix_data, mvp_clips, output_type):
    """
    given a list in the form
    [('line 1': {'begin': start, 'end': end, 'clip': file}), ...]

    return the moviepy clip resulting of concatenate each fragment from the proper clip
    """
    concatenate = (
        concatenate_videoclips if output_type == 'video' else concatenate_audioclips
    )
    segments = []
    for _, segment_data in remix_data:
        clip = mvp_clips[segment_data['clip']]
        segment = clip.subclip(segment_data['begin'], segment_data['end'])
        segments.append(segment)

    return concatenate(segments)


def get_fragments_database(mvp_clips, transcripts, remix, debug=False, force_language=None):
    """
    :parameter clips: list of input clip filenames
    :parameter transcripts: raw texts of transcripts. map one-one to clips
    :remix: list of remix lines dictionaries as returned by :func:`fine_tuning`

    """
    sources_by_clip = OrderedDict()
    remix_lines = list(remix.keys())
    for clip, transcript in zip(mvp_clips, transcripts):
        transcript = open(transcript).read().replace('\n', ' ').replace('  ', ' ')
        sources_by_clip[clip], remix_lines = fragmenter(transcript, remix_lines, debug=debug)
        if not remix_lines:
            break
    else:
        if remix_lines:
            raise DocoptExit(
                "Remix verse/s not found in transcripts given:\n{}".format('\n- '.join(remix_lines))
        )

    # create Task object

    fragments = OrderedDict()
    for clip, sources in sources_by_clip.items():
        l_sources = len(sources)
        for i, source in enumerate(sources, 1):
            if force_language:
                language = force_language
            elif i == 1:
                # for first iteration of the clip, autodetect the language
                snippet = source[:source.index(' ', 100)]
                language = langdetect.detect(snippet)
                logging.info("Autodetected language for %s: %s", clip, language)

            config_string = u"task_language={}|is_text_type=plain|os_task_file_format=json".format(language)
            with tempfile.NamedTemporaryFile('w', delete=False) as f_in:
                f_in.write(source)
            output_json = '{}.json'.format(f_in.name)
            logging.info('Forcing aligment for %s (step %s/%s)', clip, i, l_sources)
            ExecuteTaskCLI(use_sys=False).run(arguments=[
                None,
                os.path.abspath(clip),
                f_in.name,
                config_string,
                output_json
            ])
            output = json.load(open(output_json))
            for f in output['fragments']:
                line = f['lines'][0]
                try:
                    offset_begin = remix[line]['offset_begin']
                    offset_end = remix[line]['offset_end']
                except KeyError:
                    offset_begin = 0
                    offset_end = 0

                fragments.update({
                    line: {
                        'begin': float(f['begin']) + offset_begin,
                        'end': float(f['end']) + offset_end,
                        'clip': clip
                    }
                })
    return fragments

def ensure_audio(clip):
    if isinstance(clip, AudioFileClip):
        return clip
    elif isinstance(clip, VideoFileClip):
        return clip.audio


def miau(clips, transcripts, remix, output_file=None, dump=None, debug=False, force_language=None, **kwargs):
    if not output_file:
        # default to a video with the same filename than the remix
        output_file = '{}.mp4'.format(os.path.basename(remix).rsplit('.')[0])

    # map input files to moviepy clips
    mvp_clips = OrderedDict()
    for filename in clips:
        try:
            clip = VideoFileClip(filename)
        except KeyError:
            clip = AudioFileClip(filename)
        mvp_clips[filename] = clip

    output_type = extensions_dict[os.path.basename(output_file).rsplit('.')[1]]['type']

    if output_type == 'video' and not all(isinstance(clip, VideoFileClip) for clip in mvp_clips.values()):
        logging.error("Output expect to be a video but input clips aren't all videos")
        return
    elif output_type == 'audio':
        # cast clips to audio if needed
        mvp_clips = OrderedDict([(k, ensure_audio(v)) for k, v in mvp_clips.items()])

    with open(remix) as remix_fh:
        try:
            # read data from a json file (as generated by --dump option)
            # this skip the aligment
            remix_data = json.load(remix_fh)
        except json.JSONDecodeError:
            remix_fh.seek(0)
            remix_lines = OrderedDict()
            for l in remix_fh:
                if not l.strip():
                    continue
                remix_lines.update(fine_tuning(l))
            fragments = get_fragments_database(
                clips, transcripts, remix_lines,
                debug=debug, force_language=force_language
            )
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
    import ipdb; ipdb.set_trace()
    if args['--debug']:
        logging.debug(args)

    # from the whole input bag, split media files from transcriptions
    # media and its transcript must be paired (i.e same order)
    # for example, supose a folder with a video file macri_gato.mp4 and
    # its transcription is macri_gato.txt
    #
    #  -i *.mp4 *.txt
    #  -i macri_gato.*
    #  -i macri_gato.mp4 macri_gato.txt
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
    logging.info(info)
    if not media or len(media) != len(transcripts):
        raise DocoptExit(
            "Input mismatch: the quantity of inputs and transcriptions differs"
        )

    return miau(
        media,
        transcripts,
        args['--remix'],
        args['--output'],
        args['--dump'],
        debug=args['--debug'],
        force_language=args['--lang']
    )

if __name__ == '__main__':
    main()