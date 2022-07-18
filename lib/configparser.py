import yaml
import os


_CURDIR = os.path.dirname(os.path.abspath(__file__))
_HOMEDIR = os.sep.join(_CURDIR.split(os.sep)[:-1])
_CFGPATH = _HOMEDIR
_cfgfile = os.path.join(_CFGPATH, 'config.yml')


def _get_all_conf():
    result = {}
    if os.path.isfile(_cfgfile):
        try:
            result = yaml.load(open(_cfgfile), Loader=yaml.FullLoader)
        except Exception as e:
            raise RuntimeError('Load config file failed: ' + str(e))
    return result


config = _get_all_conf()


def get_utool():
    return config['utool']


def get_flashcfg(flashtype):
    return config[flashtype]


def get_hostinfo():
    return config['HOSTINFO']


if __name__ == '__main__':
    print(get_utool())
    print(get_flashcfg('BIOS'))


