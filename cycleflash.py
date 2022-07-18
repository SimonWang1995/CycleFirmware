from __future__ import print_function
import os
import random
import ipaddress
import argparse
import json
import time
import datetime
import re
import logging
from textwrap import dedent
from lib.utils import excute
from lib.logreport import put_log
from lib.configparser import get_utool, get_flashcfg, get_hostinfo


HOMEDIR = os.path.dirname(os.path.abspath(__file__))
LOGDIR = os.path.join(HOMEDIR, 'reports')
IMGDIR = os.path.join(HOMEDIR, 'images')
logger = logging.getLogger(__name__)


class FirmwareFlash:
    """
    uTool outband Flash Firmware
    request one arg flashtype
    flashtype Choice from BIOS/BMC/CPLD/PSU
    """
    def __init__(self, flashtype, **kwargs):
        self.uTool = get_utool()
        if not os.path.isfile(self.uTool):
            raise RuntimeError('No Such Utool:' + self.uTool)
        self.flashtype = flashtype
        self.bmc_cfg = kwargs
        self.flashlog = 'Flash.log'
        self.err_keys = [
            'error',
            'fail',
            'lost',
            'drop',
            'fatal'
        ]

    def flash(self, image):
        """Flash Firmware, Request a arg: image"""
        if not os.path.exists(image):
            raise RuntimeError("No Such Image: " + image)
        flashcmd = '{uTool} -H {ip} -U {username} -P {password} fwupdate -u {image} -t {flashtype} -e auto'.format(
            uTool=self.uTool, image=image, flashtype=self.flashtype, **self.bmc_cfg
        )
        logger.info('Starting Flash as following Info:')
        logger.info(' - Flash Tool Path: ' + self.uTool)
        logger.info(' - Current Location: ' + os.getcwd())
        logger.info(' - Execute Command:')
        logger.info('   ' + flashcmd)
        put_log(self.flashlog, 'Flash {0} Image: {1}\n'.format(self.flashtype, image))
        try:
            out, err = excute(flashcmd)
            res = re.search("({.*})", out, re.I|re.M|re.S).group()
            res = json.loads(res)
            put_log(self.flashlog, out)
            logger.info(' - Execute Result:')
            logger.info('   ' + str(res))
            return res
        except RuntimeError as e:
            logger.error(e)

    def getver(self):
        """Get Firmware Version"""
        self.getvercmd = '{uTool} -H {ip} -U {username} -P {password} getfw'.format(
            uTool=self.uTool, **self.bmc_cfg
        )
        out = os.popen(self.getvercmd).read()
        ver_list = json.loads(out)['Message'][0]['Firmware']
        for fw in ver_list:
            if self.flashtype in fw['Name']:
                return fw['Version']
        raise RuntimeError('No Found Firmware Version : ' + self.flashtype)


class CycleFlash(FirmwareFlash):
    """
    Utool Outband Cycle Flash Firmware(BIOS/CPLD/BMC/PSU)
    Upgrade Image or Download Image Random choice from config file
    Request a arg: flashtype choice BIOS/BMC/CPLD/PSU
    """
    def __init__(self, flashtype, loops, **kwargs):
        super().__init__(flashtype, **kwargs)
        self.loops = loops
        self.flashcfg = get_flashcfg(flashtype)
        logger.info(str(json.dumps(self.flashcfg, indent=4)))
        self.op_list = ['upgrade', 'download']
        self.split_line = "="*80
        self.res_list = []
        self.res = {}
        self.failcount = 0
        self.passcount = 0
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
        """Random choice Flash Image
        Request a arg : operate type (upgrade/download)
        return image, version"""
        image = ''
        version = ''
        image_list = self.flashcfg[op]
        # print(image_list)
        image_num = len(image_list)
        if image_num > 1:
            imageinfo = random.choice(image_list)
            image = imageinfo['image']['name']
            if not os.path.isabs(image):
                image = os.path.join(IMGDIR, image)
            version = imageinfo['image']['version']
            return image, version
        else:
            imageinfo = image_list[0]
            image = imageinfo['image']['name']
            if not os.path.isabs(image):
                image = os.path.join(IMGDIR, image)
            version = imageinfo['image']['version']
            return image, version

    def activemode(self):
        IPMI = 'ipmitool -I lanplus -H {ip} -U {username} -P {password}'.format(**self.bmc_cfg)
        powercycle = IPMI + ' chassis power cycle'
        powerstatus = IPMI + ' chassis power status'
        if self.flashtype in ['CPLD', 'BIOS']:
            logger.info('Starting Power Cycle Trigger Firmware Active')
            logger.info(' - Excute Command: ' + powercycle)
            out, err = excute(powercycle)
            logger.info(' - Command Return: ' + out)
        else:
            pass

    def wait_active(self):
        HOSTINFO = get_hostinfo()
        HOSTIP = HOSTINFO['ip']
        wait_os_up = 1200
        wait_bmc_up = 80
        flag = False
        if self.flashtype in ['CPLD', 'BIOS']:
            logger.info('Waiting {0} Seconds for Host Up'.format(str(wait_os_up)))
            time.sleep(wait_os_up)
            for i in range(10):
                if not os.system('ping -c 1 {0} > /dev/null 2>&1'.format(HOSTIP)):
                    flag = True
                    break
                logger.info('Retry Connect Host {0} times'.format(str(i)))
                time.sleep(5)
            # raise RuntimeError('Host is Hang, Can\'t Ping Host:' + HOSTIP)
        else:
            logger.info('Waiting {0} Seconds for BMC Up'.format(str(wait_os_up)))
            time.sleep(wait_bmc_up)
            for i in range(10):
                # if os.system('ping -c 1 {0} > /dev/null 2>&1'.format(HOSTIP)):
                #     flag = True
                #     break
                logger.info('Retry Connect BMC {0} times'.format(str(i)))
                time.sleep(5)
            raise RuntimeError('BMC is dead')

    def check(self):
        pass

    def compare_ver(self, criteria_ver, current_ver):
        res = ''
        logger.info('Starting Compare Firmware Version')
        logger.info(' - Current: ' + current_ver)
        logger.info(' - Criteria: ' + criteria_ver)
        if criteria_ver == current_ver:
            res = 'PASS'
            logger.info('Compare PASS')
        else:
            res = 'FAIL'
            logger.error('Compare FAIL')
        return res

    def summary(self):
        for res in self.res_list:
            if res['Result'] is 'PASS':
                self.passcount += 1
            else:
                self.failcount += 1
        tmp = dedent(
            """
            {0}
            Pass Count: {1}
            Fail Count: {2}
            Fail Rate:  {3}
            """
        )
        msg = tmp.format(self.split_line, str(self.passcount), str(self.failcount),
                         str(self.failcount/(self.failcount+self.passcount)))

    def run(self):
        for count in range(1, self.loops+1):
            self.res['Count'] = count
            op = self.op_list[count % 2]
            self.res['Operate'] = op
            # logger.info('Flash {0} Times: {1}'.format(self.flashtype, str(count)))
            pre_ver = self.getver()
            self.res['Pre Version'] = pre_ver
            flashimage, flashversion = self.select_image(op)
            self.res['Upgrade Version'] = flashversion
            self.res['Upgrade Image'] = flashimage
            logger.info(self.template.format(self.split_line, str(count), self.flashtype,
                                             op, pre_ver, flashversion, flashimage))
            put_log(self.flashlog, self.split_line)
            put_log(self.flashlog, 'N0. {0} Flash {1} firmware {2}\n'.format(str(count), self.flashtype, op))
            flash_res = self.flash(flashimage)
            self.activemode()
            self.wait_active()
            cur_ver = self.getver()
            self.res['Current Version'] = cur_ver
            compare_res = self.compare_ver(flashversion, cur_ver)
            self.res['Result'] = compare_res
            put_log(self.summary_log, str(datetime.datetime.now()) + str(self.res))
            self.res_list.append(self.res)
        self.summary()


if __name__ == '__main__':
    pass



