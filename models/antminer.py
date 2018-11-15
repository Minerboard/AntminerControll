import requests
from re import search
from datetime import datetime
from models.miner import Miner
from requests.auth import HTTPDigestAuth
from models.lib.pycgminer import get_stats, get_pools
from time import sleep


class Antminer(Miner):

    def __init__(self, ip, login='root', password='root'):
        Miner.__init__(self, ip, login, password)
        self.__stats = {}
        self.existence = False
        self.__get_stats()
        if self.existence:
            self.__total_chips = 0
            self.__o_chips = 0
            self.__x_chips = 0
            self.__i_chips = 0
            self.__last_scanned = None
            self.get_type()
            self.__get_pools()
            self.get_temps()
            self.get_fans()
            self.get_rates()
            self.get_chips()

    def __get_stats(self):
        """Using custom pycgminer lib and miner ip address connect to antminer [STATS] api"""
        miner_stats = get_stats(self.ip)
        if not miner_stats:
            self.existence = False
        elif miner_stats['STATUS'][0]['STATUS'] != 'error':
            self.existence = True
            self.__stats = dict(miner_stats)
            self.set_status(self.__stats['STATUS'][0]['STATUS'])
        else:
            self.existence = False

    def __get_pools(self):
        """Using custom pycgminer lib and miner ip address connect to antminer [POOLS] api"""
        miner_pools = get_pools(self.ip)
        worker_list = []
        url_list = []
        if not miner_pools:
            self.set_worker(None)
            self.set_url(None)
            return
        for i in miner_pools['POOLS']:
            worker_list.append(i["User"])
            url_list.append(i["URL"])
        self.set_worker(worker_list)
        self.set_url(url_list)

    def get_type(self):
        """get from api and set antminer model type"""
        self.set_type(self.__stats["STATS"][0]['Type'])

    def get_fans(self):
        """get from api and set antminer fan (list)"""
        if not self.__stats:
            return 0
        fan_speeds = [
            self.__stats['STATS'][1][fan] for fan in sorted(
                self.__stats['STATS'][1].keys(), key=lambda x: str(x))
            if search("fan" + '[0-9]', fan)
            if self.__stats['STATS'][1][fan] != 0
        ]
        self.set_fans(fan_speeds)

    def get_temps(self):
        """get from api and set antminer temp (list)"""
        if not self.__stats:
            return 0
        temps = [
            int(self.__stats['STATS'][1][temp]) for temp in sorted(
                self.__stats['STATS'][1].keys(), key=lambda x: str(x))
            if search('temp' + '[0-9]', temp)
            if int(self.__stats['STATS'][1][temp]) != 0
        ]
        self.set_temp(temps)

    def get_rates(self):
        """get from api and set antminer hashrate (list)"""
        if not self.__stats:
            return 0
        # rates = 0
        # for rate in sorted(self.__stats['STATS'][1].keys(), key=lambda x: str(x)):
        #     if search('chain_rate' + '[0-9]', rate) and (self.__stats['STATS'][1][rate]) and (self.__stats['STATS'][1][rate] != '0.0'):
        #         rates = [float(self.__stats['STATS'][1][rate])]

        self.set_rate(float(self.__stats['STATS'][1]['GHS 5s']))

    def get_chips(self):
        if not self.__stats:
            return 0
        asic_chains = [
            self.__stats['STATS'][1][chain]
            for chain in self.__stats['STATS'][1].keys()
            if "chain_acs" in chain
        ]
        # count number of working chips
        self.__x_chips = [str(o).count('o') for o in asic_chains]
        self.__o_chips = sum(self.__x_chips)
        # count number of defective chips
        self.__x_chips = [str(x).count('x') for x in asic_chains]
        self.__x_chips = sum(self.__x_chips)
        # get number of in-active chips
        self.__i_chips = [str(x).count('-') for x in asic_chains]
        self.__i_chips = sum(self.__i_chips)
        # get total number of chips
        self.__total_chips = self.__o_chips + self.__x_chips + self.__i_chips


    def configure_asic(self, pool, name, token, fan_speed=''):
        # print(r''+pool+name+token)
        url = 'http://{0}/cgi-bin/set_miner_conf.cgi'.format(self.ip)
        data = {'_ant_pool1url': pool,
                '_ant_pool1user': name,
                '_ant_pool1pw': token,
                '_ant_pool2url': pool,
                '_ant_pool2user': name,
                '_ant_pool2pw': token,
                '_ant_pool3url': pool,
                '_ant_pool3user': name,
                '_ant_pool3pw': token,
                '_ant_nobeeper': 'false',
                '_ant_notempoverctrl': 'false',
                '_ant_fan_customize_switch': 'false',
                '_ant_fan_customize_value': fan_speed}
        try:
            requests.post(url, data=data, timeout=3, auth=HTTPDigestAuth(self.login, self.password))
        except Exception:
            return False
        else:
            self.__last_scanned = str(datetime.today().replace(microsecond=0))
            return True

    def reboot(self,time='3'):
        """ Using personal antminer login and password
            reboot antminer via get request"""
        url = 'http://{0}/cgi-bin/reboot.cgi?_={1}'.format(self.ip, time)

        try:
            requests.get(url, timeout=3, auth=HTTPDigestAuth(self.login, self.password))
        except:
            return False
        else:
            return True

    @property
    def last_scanned(self):
        return self.__last_scanned

    @property
    def total_chips(self):
        return self.__total_chips

    @property
    def o_chips(self):
        return self.__o_chips

    @property
    def x_chips(self):
        return self.__x_chips

    @property
    def i_chips(self):
        return self.__i_chips