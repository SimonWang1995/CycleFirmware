import os
import shutil
import logging
from textwrap import dedent


CURDIR = os.path.dirname(os.path.abspath(__file__))
HOMEDIR = os.sep.join(CURDIR.split(os.sep)[:-1])
LOGPATH = os.path.join(HOMEDIR, 'reports')


def delreports():
    if os.listdir(LOGPATH):
        ans = input('Reports is exist,Delete Reports [Y/N]:')
        if ans.lower() in ['y', 'yes']:
            for file in os.listdir(LOGPATH):
                logfile = os.path.join(LOGPATH, file)
                if os.path.isdir(logfile):
                    shutil.rmtree(os.path.join(LOGPATH, file))
                else:
                    os.remove(logfile)


def initlogger(file):
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.DEBUG)
    logfile = os.path.join(LOGPATH, file)
    hander = logging.FileHandler(logfile)
    hander.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    hander.setFormatter(formatter)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    logger.addHandler(console)
    logger.addHandler(hander)
    return logger


def put_log(filename, msg):
    file = os.path.join(LOGPATH, filename)
    with open(file, 'a') as f:
        f.write(msg + '\n')


if __name__ == '__main__':
    initlogger('test.log')
