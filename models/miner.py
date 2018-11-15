class Miner(object):
    def __init__(self, ip, login, password):
        self.__ip = ip
        self.__login = login
        self.__password = password
        self.__type = ""
        self.__workers = []
        self.__urls = []
        self.__temps = []
        self.__fans = []
        self.__rates = 0.0
        self.__status = False

    def __str__(self):
        return str(self.__ip + self.__login + self.__password + self.__type + self.__workers + self.__urls)

    def set_type(self, name):
        self.__type = name

    def set_status(self, status):
        self.__status = status

    def set_worker(self, worker_list):
        if isinstance(worker_list, list):
            self.__workers = worker_list[0]
        else:
            self.__workers = worker_list

    def set_url(self, url_list):
        if isinstance(url_list, list):
            self.__urls = url_list[0]
        else:
            self.__urls = url_list

    def set_fans(self, fan):
        self.__fans = fan

    def set_temp(self, temp):
        self.__temps = temp

    def set_rate(self, rate):
        self.__rates = rate

    def set_login(self,login):
        self.__login = login

    def set_password(self, password):
        self.__password = password

    @property
    def ip(self):
        return self.__ip

    @property
    def login(self):
        return self.__login

    @property
    def password(self):
        return self.__password

    @property
    def type(self):
        return self.__type

    @property
    def worker(self):
        return self.__workers

    @property
    def pool(self):
        return self.__urls

    @property
    def fan(self):
        if not len(self.__fans):
            return 0
        return round(sum(self.__fans)/len(self.__fans), 1)

    @property
    def temp(self):
        if not len(self.__temps):
            return 0
        return round(sum(self.__temps)/len(self.__temps), 1)

    @property
    def rate(self):
        return round(self.__rates, 1)

    @property
    def status(self):
        return self.__status
