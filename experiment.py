# coding=utf8

from functools import partial
import contextlib
import logging
import os
import sh
import shutil
import sys
import tempfile
import time

COUNT = 1
LINE = '-'*80
VIRTUALENV_PATH = '/home/rafaelbc//trt3/trt3plone/python_buildout/python-2.7/bin/virtualenv'
ZC_RECIPE_EGG_PATH = '/home/rafaelbc/data/checkouts/git/buildout/zc.recipe.egg_'
ZC_RECIPE_EGG_PUBLISHED_REV = '1c8a5ea8f206137b8708053d77b55ba0cf1f07b1'


def setup_logging():
    u"""Setup logging for use in CLI scripts."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
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


def time_buildout(buildout_path, options=()):
    python_cmd = sh.Command('bin/python')
    args = [
        'time_buildout.py',
        buildout_path,
        '--count={}'.format(COUNT),
        '--virtualenv={}'.format(VIRTUALENV_PATH),
        '--develop={}'.format(ZC_RECIPE_EGG_PATH),
    ]
    if options:
        args.append('--')
        args.extend(options)
    python_cmd(*args, _out=sys.stdout, _err_to_out=True)


def checkout_zc_recipe_egg(rev):
    with cd(ZC_RECIPE_EGG_PATH):
        sh.git.checkout(rev)


def test_buildout(name, time_buildout_func):
    logger = logging.getLogger('test_buildout')
    logger.info('Using buildout: {}'.format(name))
    logger.info('Using zc.recipe.egg version: published on PyPI')
    checkout_zc_recipe_egg(ZC_RECIPE_EGG_PUBLISHED_REV)
    time_buildout_func()
    logger.info('Using zc.recipe.egg version: pull request')
    checkout_zc_recipe_egg('master')
    time_buildout_func()


def test_simple_buildout():
    name = 'simple_buildout'
    test_buildout(name, partial(time_buildout, name))


def test_plone_deploy_buildout(num_extra_instances):
    buildout_name = 'plone_deploy_buildout'
    friendly_name = '{} with {} extra instances'.format(buildout_name, num_extra_instances)
    test_buildout(
        friendly_name,
        partial(
            time_buildout,
            buildout_name,
            options=['instance-multiplier:count={}'.format(num_extra_instances)]
        )
    )


def main():
    setup_logging()
    logger = logging.getLogger('main')
    logger.info('Begin.')

    test_simple_buildout()
    test_plone_deploy_buildout(1)
    test_plone_deploy_buildout(2)

    logger.info('End.')


if __name__ == '__main__':
    main()
