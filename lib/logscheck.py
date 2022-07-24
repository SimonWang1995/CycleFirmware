class LogsCheck(object):
    def __init__(self, **kwargs):
        self.IPMI = "ipmitool -I lanplus -H {ip} -U {username} -P {password}".format(**kwargs)

    def init_first(self):
        pass

    def get_logs(self, count):
        pass

    def compare_log(self):
        pass