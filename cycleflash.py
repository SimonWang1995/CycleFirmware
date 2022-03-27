from __future__ import print_function
import os
import random
import ipaddress
import argparse
import json
import time
from textwrap import dedent
from lib.utils import excute
from lib.logreport import initlogger, delreports, put_log
from lib.configparser import ConfigParser


HOMEDIR = os.path.dirname(__file__)
LOGDIR = os.path.join(HOMEDIR, 'reports')
IMGDIR = os.path.join(HOMEDIR, 'images')


class FirmwareFlash:
    def __init__(self, flashtype):
        self.uTool = uTool
        self.flashtype = flashtype
        self.flashlog = 'Flash.log'
        self.err_keys = [
            'error',
            'fail',
            'lost',
            'drop',
            'fatal'
        ]

    def flash(self, image):
        if not os.path.isabs(image):
            image = os.path.join(IMGDIR, image)
        if not os.path.exists(image):
            raise RuntimeError("No Such Image: " + image)
        flashcmd = '{uTool} -H {ip} -U {username} -P {password} fwupdate -u {image} -t {flashtype} -e auto'.format(
            uTool=self.uTool, image=image, **args
        )
        logger.info('Starting Flash as following Info:')
        logger.info(' - Flash Tool Path: ' + self.uTool)
        logger.info(' - Current Location: ' + os.getcwd())
        logger.info(' - Execute Command:')
        logger.info('   ' + flashcmd)
        put_log(self.flashlog, 'Flash {0} Image: {1}'.format(self.flashtype, image))
        try:
            out, err = excute(flashcmd)
            put_log(self.flashlog, out)
        except RuntimeError as e:
            logger.error(e)

    def getver(self):
        self.getvercmd = '{uTool} -H {ip} -U {username} -P {password} getfw'.format(
            uTool=self.uTool, **args
        )
        out = os.popen(self.getvercmd).read()
        ver_list = json.loads(out)['Firmware']
        for fw in ver_list:
            if self.flashtype in fw['Type']:
                return fw['Version']


class CycleFlash(FirmwareFlash):
    def __init__(self, flashtype):
        super().__init__(flashtype)
        self.flashcfg = config.get_flashcfg(flashtype)
        self.op_list = ['upgrade', 'download']
        self.split_line = "="*80
        self.summary_log = 'summary_result.log'
        self.template = dedent("""
                               {0}
                               Run Flash Cycle:  {1}
                               Flash Device:     {2}
                               FLash Operation:  {3}
                               Current Version:  {4}
                               Upgrade Version:  {5}
                               Upgrade Firmware: {6}
                               """)

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
        powercycle = IPMI + ' chassis power cycle'
        powerstatus = IPMI + ' chassis power status'
        if self.flashtype in ['cpld', 'bios']:
            logger.info('Excute Command: ' + powercycle)
            out, err = excute(powercycle)
            logger.info(out)
        else:
            pass

    def wait_active(self):
        os_up = 600
        bmc_up = 80
        flag = False
        if self.flashtype in ['cpld', 'bios']:
            time.sleep(os_up)
            for i in range(10):
                if os.system('ping -c 1 {0} > /dev/null 2>&1'.format(HOSTIP)):
                    flag = True
                    break
                time.sleep(5)
        else:
            time.sleep(bmc_up)
            for i in range(10):
                pass

    def check(self):
        pass

    def compare_ver(self, criteria_ver, current_ver):
        logger.info(' - Current: ' + current_ver)
        logger.info(' - Criteria: ' + criteria_ver)
        put_log(' - Current: ' + current_ver)
        put_log(' - Criteria: ' + criteria_ver)
        if criteria_ver == current_ver:
            logger.info('Version Compare: PASS')
            put_log('Version Compare: PASS')
        else:
            logger.error("Version Compare: FAIL")
            put_log("Version Compare: FAIL")

    def summary(self):
        pass

    def run(self):
        for count in range(1, loops*2):
            op = self.op_list[count % 2]
            cycle = (count+1) // 2
            logger.info('Flash {0} Times: {1}'.format(self.flashtype, str(cycle)))
            pre_ver = self.getver()
            flashimage, flashversion = self.select_image(op)
            logger.info(self.template.format(self.split_line, str(cycle), self.flashtype,
                                             op, pre_ver, flashversion, flashimage))
            put_log(self.flashlog, 'N0. {0} Flash {1} firmware {2}'.format(str(cycle), self.flashtype, op))
            self.flash(flashimage)
            self.activemode()
            self.wait_active()
            put_log('NO. {0} Flash {1} firmware {2}'.format(str(cycle), self.flashtype, op))
            self.compare_ver(flashversion, self.getver())
        self.summary()


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
    HOSTIP = '192.168.0.35'
    IPMI = 'ipmitool -I lanplus -H {ip} -U {username} -P {password}'.format(**args)
    # if os.system(IPMI + ' raw 6 1 > /dev/null 2>&1'):
    #     raise RuntimeError('Check BMC Overlan Fail, Please Check BMC Info.')
    config = ConfigParser(os.path.join(HOMEDIR, 'config.yml'))
    uTool = config.get_utool()
    # if not os.path.exists(uTool):
        # raise RuntimeError('No Such Utool:' + uTool)
    # flash_cfg = config.get_flashcfg(flashtype)
    # up_images = flash_cfg['upgrade']
    # down_images = flash_cfg['download']
    delreports()
    logger = initlogger('CycleFlash.log')
    cycleflasher = CycleFlash(flashtype)
    cycleflasher.run()



