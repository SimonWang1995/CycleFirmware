import yaml


class ConfigParser:
    def __init__(self, file):
        self.config = yaml.load(open(file), Loader=yaml.FullLoader)
        # print(self.config)

    def get_utool(self):
        return self.config['utool']

    def get_flashcfg(self, flashtype):
        return self.config[flashtype]


if __name__ == '__main__':
    config = ConfigParser('../config.yml')


