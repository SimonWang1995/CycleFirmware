import os
import shutil
import logging
from textwrap import dedent


_CURDIR = os.path.dirname(os.path.abspath(__file__))
_HOMEDIR = os.sep.join(_CURDIR.split(os.sep)[:-1])
_LOGPATH = os.path.join(_HOMEDIR, 'reports')
_filename = 'CycleFlash.log'


def delreports():
    if os.listdir(_LOGPATH):
        ans = input('Reports is exist,Delete Reports [Y/N]:')
        if ans.lower() in ['y', 'yes']:
            for file in os.listdir(_LOGPATH):
                logfile = os.path.join(_LOGPATH, file)
                if os.path.isdir(logfile):
                    shutil.rmtree(os.path.join(_LOGPATH, file))
                else:
                    os.remove(logfile)


def init_log():
    logger = logging.getLogger()
    logger.setLevel(level=logging.DEBUG)
    logfile = os.path.join(_LOGPATH, _filename)
    hander = logging.FileHandler(logfile)
    hander.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    hander.setFormatter(formatter)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    logger.addHandler(console)
    logger.addHandler(hander)


def put_log(filename, msg):
    file = os.path.join(_LOGPATH, filename)
    with open(file, 'a') as f:
        f.write(msg + '\n')


if __name__ == '__main__':
    init_log()
    logger = logging.getLogger(__name__)
    logger.info('test log ........')
