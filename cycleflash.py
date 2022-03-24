from __future__ import print_function
import os
import random
import ipaddress
import argparse
from lib.configparser import ConfigParser


HOMEDIR = os.path.dirname(__file__)


class FirmwareFlash:
    def __init__(self, flashtype):
        self.uTool = uTool
        self.flashtype = flashtype

    def flash(self, image):
        flashcmd = '{uTool} -H {ip} -U {username} -P {password} fwupdate -u {image} -t {flashtype} -e auto'.format(
            uTool=self.uTool, image=image, **args
        )
        out = os.popen(flashcmd)
        return out.read()

    def getver(self):
        pass


class CycleFlash(FirmwareFlash):
    def __init__(self, flashtype):
        super().__init__(flashtype)
        self.flashcfg = config.get_flashcfg(flashtype)
        self.op_list = ['upgrade', 'download']

    def select_image(self, op):
        image = ''
        version = ''
        image_list = self.flashcfg[op]
        print(image_list)
        image_num = len(image_list)
        if image_num > 1:
            imageinfo = random.choice(image_list)
            image = imageinfo['image']['name']
            version = imageinfo['image']['version']
            return image, version
        else:
            imageinfo = image_list[0]
            image = imageinfo['image']['name']
            version = imageinfo['image']['version']
            return image, version

    def activemode(self):
        pass

    def wait_active(self):
        pass

    def run(self):
        for count in range(1, loops*2):
            op = self.op_list[count % 2]
            image, version = self.select_image(op)
            self.flash(image)
            self.activemode()
            self.wait_active()
            if version == self.getver():
                pass


def _argparser():
    parser = argparse.ArgumentParser(description='This is Cycle Flash Program')
    parser.add_argument('-t', '--type', action='store', dest='flashtype', choices=['bios', 'bmc', 'cpld', 'psu'],
                        required=True, help='Flash type')
    parser.add_argument('-c', '--cycle', type=int, dest='loops', default=100, help='input flash times')
    group = parser.add_argument_group('BMC Info', description='This is BMC Info')
    group.add_argument('-H', dest='ip', type=ipaddress.ip_address, required=True, help='BMC Ip Address')
    group.add_argument('-U', dest='username', required=True, help='BMC User Name')
    group.add_argument('-P', dest='password', required=True, help='BMC Password')
    return parser.parse_args().__dict__

if __name__ == '__main__':
    args = _argparser()
    flashtype = args['flashtype']
    loops = args['loops']
    IPMI = 'ipmitool -I lanplus -H {ip} -U {username} -P {password}'.format(**args)
    # if os.system(IPMI + ' raw 6 1 > /dev/null 2>&1'):
    #     raise RuntimeError('Check BMC Overlan Fail, Please Check BMC Info.')
    config = ConfigParser(os.path.join(HOMEDIR, 'config.yml'))
    uTool = config.get_utool()
    # if not os.path.exists(uTool):
        # raise RuntimeError('No Such Utool:' + uTool)
    cycleflasher = CycleFlash(flashtype)
    cycleflasher.run()



