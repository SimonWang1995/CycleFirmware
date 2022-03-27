import os
import logging
import subprocess


def excute(*cmd, **kwargs):
    obj = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, shell=True)
    out, err = obj.communicate()
    _ret_code = obj.returncode
    if _ret_code or err:
        raise RuntimeError('Error: {0}, exit code: {1}'.format(err, _ret_code))
    return (out, err)
