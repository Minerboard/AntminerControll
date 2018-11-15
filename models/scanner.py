from models.lib.util import Util
from models.antminer import Antminer


class ASICScanner:
    def __init__(self, start_ip, end_ip):
        self.__start_ip = start_ip
        self.__end_ip = end_ip
        self.__templates = []
        self.ip = None
        self.status = False
        self.__stop_trigger = False

    def control_range_scan(self):
        self.__stop_trigger = False
        ip_range = self.__scan_ip_range()
        if ip_range:
            Util.add_asics_json(asic_list=ip_range)
            self.status = True

    def __scan_ip_range(self):
        """ :start_ip - str IPv4 address
            :end_ip - str IPv4 address
            Scans Network in :start_ip :end_ip range and check hostname
            Returns ip and hostname (if exists)"""
        start = list(map(int, self.__start_ip.split(".")))
        end = list(map(int, self.__end_ip.split(".")))
        temp = start
        ip_range = []

        start[3] -= 1
        while temp != end:
            start[3] += 1
            for i in (3, 2, 1):
                if temp[i] == 256:
                    temp[i] = 0
                    temp[i - 1] += 1
            ip = ".".join(map(str, temp))
            if self.__stop_trigger:
                break
            asic_obj = Antminer(ip)
            print(asic_obj.ip,asic_obj.existence)
            if asic_obj.existence:
                ip_range.append(asic_obj.ip)
                del asic_obj

        return ip_range


    def stop(self):
        self.__stop_trigger = True