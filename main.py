import logging
import ipaddress
import argparse
import os
from lib.logreport import init_log, delreports
from cycleflash import CycleFlash

logger = logging.getLogger(__name__)


def _argparser():
    parser = argparse.ArgumentParser(description='This is Cycle Flash Program')
    parser.add_argument('-t', '--type', action='store', dest='flashtype', choices=['BIOS', 'BMC', 'CPLD', 'PSU'],
                        required=True, help='Flash type')
    parser.add_argument('-c', '--cycle', type=int, dest='loops', default=100,
                        help='input flash times(default:%(default)s')
    group = parser.add_argument_group('BMC Info', description='This is BMC Info')
    group.add_argument('-H', dest='ip', type=ipaddress.ip_address, required=True, help='BMC Ip Address')
    group.add_argument('-U', dest='username', required=True, help='BMC User Name')
    group.add_argument('-P', dest='password', required=True, help='BMC Password')
    return parser.parse_args().__dict__


def main():
    args = _argparser()
    flashtype = args['flashtype']
    loops = args['loops']
    bmc_cfg = {}
    bmc_cfg['ip'] = args['ip']
    bmc_cfg['username'] = args['username']
    bmc_cfg['password'] = args['password']
    IPMI = 'ipmitool -I lanplus -H {ip} -U {username} -P {password}'.format(**bmc_cfg)
    if os.system(IPMI + ' raw 6 1 > /dev/null 2>&1'):
        raise RuntimeError('Check BMC Overlan Fail, Please Check BMC Info.')
    # flash_cfg = get_flashcfg(flashtype)
    # up_images = flash_cfg['upgrade']
    # down_images = flash_cfg['download']
    delreports()
    init_log()
    cycleflasher = CycleFlash(flashtype, loops, **bmc_cfg)
    cycleflasher.run()


if __name__ == '__main__':
    main()
