import os
import logging
import subprocess

_LOG = logging.getLogger(__name__)


def excute(*cmd, **kwargs):
    _LOG.info("Excute {}".format(cmd))
    obj = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, shell=True)
    out, err = obj.communicate()
    res = (out.strip().decode('utf-8'), err.strip().decode('utf-8'))
    _ret_code = obj.returncode
    if _ret_code or err:
        raise RuntimeError('Error: {0}, exit code: {1}'.format(err, _ret_code))
    return res
