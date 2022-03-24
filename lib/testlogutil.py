import os
import shutil
import logging


CURDIR = os.path.dirname(os.path.abspath(__file__))
HOMEDIR = os.sep.join(CURDIR.split(os.sep)[:-1])
LOGPATH = os.path.join(HOMEDIR, 'reports')


def initlogger(file):
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.DEBUG)
    logfile = os.path.join(LOGPATH, file)
    hander = logging.FileHandler(logfile + '.debug')
    hander.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    hander.setFormatter(formatter)
    hander1 = logging.FileHandler(logfile)
    hander1.setLevel(logging.INFO)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    logger.addHandler(console)
    logger.addHandler(hander)
    logger.addHandler(hander1)
    return logger


def initreports():
    if os.listdir(LOGPATH):
        ans = input('Reports is exist,Delete Reports [Y/N]:')
        if ans.lower() in ['y', 'yes']:
            for file in os.listdir(LOGPATH):
                logfile = os.path.join(LOGPATH, file)
                if os.path.isdir(logfile):
                    shutil.rmtree(os.path.join(LOGPATH, file))
                else:
                    os.remove(logfile)


def put_log(file, info):
    logfile = os.path.join(LOGPATH, file)
    with open(logfile, 'a') as f:
        f.write(info)


if __name__ == '__main__':
    init()
