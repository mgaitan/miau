#!/usr/bin/env python
import os
import re
import json
import tempfile
import logging
from aeneas.executetask import ExecuteTask
from aeneas.task import Task
from aeneas.tools.execute_task import ExecuteTaskCLI
import fire


logging.basicConfig(format='[miau] %(asctime)s %(levelname)s: %(message)s',
                    level=30,
                    datefmt='%Y-%m-%d %H:%M:%S')

class CommandLine(object):
    """
    Command-line interface for miau
    """
    HOME = os.path.dirname(os.path.abspath(__file__))
    VERSION = "0.1.0"


    @classmethod
    def parse_args(cls):
        parser = argparse.ArgumentParser(description='miau Runtime',
                                         prog=__file__,
                                         add_help=False,
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                         epilog='The exit status is 0 for non-failures and 1 for failures.')

        m = parser.add_argument_group('Mandatory Arguments')
        g = m.add_mutually_exclusive_group(required=True)
        g.add_argument('-foob', metavar='foo', type=str, help='foo')

        o = parser.add_argument_group('Optional Arguments')
        o.add_argument('-verbosity', metavar='{1..5}', default=2, type=int, choices=list(range(1, 6, 1)),
                       help='Level of verbosity for logging module.')
        o.add_argument('-h', '-help', '--help', action='help', help=argparse.SUPPRESS)
        o.add_argument('-version', action='version', version='%(prog)s {}'.format(cls.VERSION), help=argparse.SUPPRESS)

        return parser.parse_args()

    @staticmethod
    def pair_to_dict(args):
        return dict(kv.split('=', 1) for kv in args)

    @classmethod
    def main(cls):
        args = cls.parse_args()

        logging.basicConfig(format='[miau] %(asctime)s %(levelname)s: %(message)s',
                            level=args.verbosity * 10,
                            datefmt='%Y-%m-%d %H:%M:%S')

        miau = miau(*miau_conf)
        try:
            pass
        except miauException as msg:
            logging.error(msg)
            return 1
        except KeyboardInterrupt:
            print('')
            logging.info("Caught SIGINT - Aborting.")
            return 0
        finally:
            logging.info("Initiating shutdown routines.")
            try:
                pass
            except miauException as msg:
                logging.error(msg)
                return 1

        return 0



def fragmenter(source, remix):
    """return as many versions of the source text
    to ensure each line of the remix appear as an independent line
    at least once"""

    # source = re.sub('^$', '[BLANK]', source, flags=re.MULTILINE)
    #source = re.sub('\n', ' ', source, flags=re.MULTILINE)
    source = source.replace('\n', ' ').replace('  ', ' ')
    # source = re.sub('\[BLANK\]', '\n', source, flags=re.MULTILINE)
    remix_lines = [l.strip() for l in remix.split('\n') if l.strip()]

    for line in remix_lines:
        if not line in source:
            logging.exception('"%s" not found in the transcript', line)


    def iterate(lines):

        current = source
        not_found = []
        for line in lines:
            if not line in current:
                not_found.append(line)
                continue
            current = current.replace(line, '{}\n'.format(line))
        current = current.replace('\n ', '\n')
        return current, not_found

    results = []
    while True:
        result, not_found = iterate(remix_lines)
        results.append(result)
        if not not_found:
            break
        remix_lines = not_found

    return results



def miau(transcript, clip, remix_script, output):
    # TODO: allow multiples transcript/videos
    sources = fragmenter(open(transcript).read(), open(remix_script).read())
    # create Task object

    config_string = u"task_language=es|is_text_type=plain|os_task_file_format=json"
    results = []
    for source in sources:
        with tempfile.NamedTemporaryFile('w', delete=False) as f_in:
            f_in.write(source)

        output_json = '{}.json'.format(f_in.name)
        import ipdb; ipdb.set_trace()
        ExecuteTaskCLI(use_sys=False).run(arguments=[
            None,
            os.path.abspath(clip),
            f_in.name,
            config_string,
            output_json
        ])
        result = json.load(open(output_json))

        results.append(result)
    return results




if __name__ == '__main__':
    result = fire.Fire(miau)
    print(result)