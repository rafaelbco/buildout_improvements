# coding=utf8
"""Time buildout execution.

Usage:
  time_buildout [options] <buildout_path> [-- <buildout_option>...]

Options:
  -h, --help                Show help.
  -c, --count=<n>           Run N times. [default: 10]
  -v, --virtualenv=<path>   Path to virtualenv script. [default: virtualenv]
  -d, --develop=<path>      Insert development egg.
"""
from docopt import docopt
import contextlib
import logging
import os
import sh
import shutil
import sys
import tempfile
import time


BUILDOUT_IGNORE_PATTERNS = shutil.ignore_patterns(
    'bin',
    'develop-eggs',
    'eggs',
    'include',
    'lib',
    'parts',
    'pip-selfcheck.json',
    '.installed.cfg',
    '.cache',
)


def setup_logging():
    u"""Setup logging for use in CLI scripts."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        '%(levelname)-7s [%(asctime)s] %(name)s: %(message)s',
        '%H:%M:%S'
    )
    handler.setFormatter(formatter)
    root_logger.handlers = [handler]
    logging.getLogger('requests').setLevel(logging.WARNING)


@contextlib.contextmanager
def cd(newdir, cleanup=lambda: True):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)
        cleanup()


@contextlib.contextmanager
def tempdir(prefix=''):
    dirpath = tempfile.mkdtemp(prefix=prefix)

    def cleanup():
        shutil.rmtree(dirpath)

    with cd(dirpath, cleanup):
        yield dirpath


@contextlib.contextmanager
def timer(name):
    start = time.time()
    yield
    elapsed = time.time() - start
    print('[{}] finished in {} s'.format(name, elapsed))


def run_buildout(buildout_path, virtualenv_path, options):
    logger = logging.getLogger('run_buildout')

    buildout_name = os.path.basename(buildout_path)
    with tempdir(prefix='time_buildout.') as temp_dir_path:
        logger.info('Working in {}'.format(temp_dir_path))
        new_buildout_path = os.path.join(temp_dir_path, buildout_name)
        shutil.copytree(src=buildout_path, dst=new_buildout_path, ignore=BUILDOUT_IGNORE_PATTERNS)

        with cd(new_buildout_path):
            virtualenv_cmd = sh.Command(virtualenv_path)
            virtualenv_cmd('.')
            pip_cmd = sh.Command('bin/pip')
            pip_cmd('install', requirement='buildout_requirements.txt')
            buildout_cmd = sh.Command('bin/buildout')

            start_time = time.time()
            buildout_cmd(options)  # _err_to_out=True, _out=sys.stdout
            duration = time.time() - start_time
            logger.info('buildout took {} s'.format(duration))
            return duration


def main():
    setup_logging()

    arguments = docopt(__doc__)
    buildout_path = os.path.abspath(arguments['<buildout_path>'])
    count = int(arguments['--count'])
    virtualenv_path = arguments['--virtualenv']
    development_egg = arguments['--develop'] or ''
    buildout_options = arguments['<buildout_option>']

    if development_egg:
        buildout_options.append('buildout:develop={}'.format(development_egg))

    def run_the_buildout(name):
        print 'Buildout run: {}'.format(name)
        duration = run_buildout(buildout_path, virtualenv_path, buildout_options)
        print '-' * 80
        return duration

    run_the_buildout('Warm up')

    durations = [run_the_buildout(str(i)) for i in xrange(1, count + 1)]

    print
    print 'Runs:'
    for (i, d) in enumerate(durations, 1):
        print '{:02d}: {} s'.format(i, d)
    print
    print 'Average: {}'.format(sum(durations) / float(len(durations)))


if __name__ == '__main__':
    main()
