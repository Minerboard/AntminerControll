from socket import gethostbyaddr
from ipaddress import ip_address
from getmac import get_mac_address
from requests import get
from json import load, dump

class Util():


    @staticmethod
    def get_host_name(ip):
        """returns host name via string ip address;
           else: None"""
        try:
            name = gethostbyaddr(ip)[0]
            return name
        except Exception:
            return None

    @staticmethod
    def get_manufacturer(mac):
        """returns device manufacturer via string MAC;
            else: None"""
        MAC_URL = 'http://macvendors.co/api/%s'
        try:
            req = get(MAC_URL % mac).json()
            result = req["result"]["company"]
        except Exception:
            return None
        return result

    @staticmethod
    def get_mac(ip):
        """returns MAC via string ip address;
            else: None"""
        try:
            ip_mac = get_mac_address(ip=ip)
            return ip_mac
        except Exception:
            return None

    @staticmethod
    def check_ipv4(address):
        """ IPV4 validation.
            :address - ip address.
            if IPV4 - returns True
            else - False"""
        try:
            result = ip_address(address)
            if result:
                return True
        except ValueError:
            return False

    @staticmethod
    def compare_ipv4(ip1, ip2):

        ip1 = list(map(int, ip1.split('.')))
        ip2 = list(map(int, ip2.split('.')))
        if ip1 < ip2:
            return True
        return False


    @staticmethod
    def add_asics_json(asic_list, filename='./devices.json',mode=0):
        data = {"devices": []}
        if mode == 0:
            data['devices'].extend(asic_list)
        elif mode == 1:
            saved_data = Util.load_asics_json()
            if saved_data:
                data['devices'].extend(saved_data)
        try:
            with open(filename, 'w') as json_file:
                dump(data, json_file)
        except Exception:
            return False
        else:
            json_file.close()
        return True

    @staticmethod
    def delete_from_json(ip,filename='./devices.json'):
        try:
            saved_data = Util.load_asics_json()
            if isinstance(saved_data, list):
                for i in saved_data:
                    if i == ip:
                        saved_data.remove(i)
                        break
            data = {"devices": []}
            data['devices'].extend(saved_data)
            with open(filename, 'w') as json_file:
                dump(data, json_file)
        except Exception:
            return False
        else:
            json_file.close()
        return True

    @staticmethod
    def cleanup_json(filename='./devices.json'):
        try:
            data = {"devices": []}
            with open(filename, 'w') as json_file:
                dump(data, json_file)
        except Exception:
            return False
        else:
            json_file.close()
            return True

    @staticmethod
    def load_asics_json(filename='./devices.json'):
        try:
            with open(filename) as json_file:
                data = load(json_file)
            print(data)
            if not data['devices']:
                return False
            print(data)
            return data['devices']
        except Exception as err:
            print(1, err)
            return False
