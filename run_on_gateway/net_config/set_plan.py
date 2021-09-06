import sys
import os
import shutil
import subprocess
from shlex import split
import yaml


class Iface:
    def __init__(self, name, hw_addr):
        self.name = name
        self.hw = hw_addr
        self.fix_ip = None
        self.dhcp = False

iface_name_file = sys.argv[1]

with open(iface_name_file, 'r') as f:
    name_list = []
    hw_addrs = []
    for line in f:
        name_list.append(line.strip())
        hw = os.popen("cat /sys/class/net/%s/address" % name_list[-1]).read().strip()
        hw_addrs.append(hw)

ether = {key:value for key,value in zip(name_list,hw_addrs)}

#print(ether)

####Config Netplan
with open("50-cloud-init.yaml", 'r') as stream:
    try:
#        plan = ruamel.yaml.load(stream, Loader=ruamel.yaml.RoundTripLoader)
        plan = yaml.load(stream, Loader=yaml.FullLoader)
        Iface_dict = plan['network']['ethernets']
        Iface_list = list(Iface_dict.keys())
    except yaml.YAMLError as exc:
        print(exc)

iface_counter = 0
for name in name_list:
    if name != 'ens3':
        iface_counter += 1
        num = iface_counter
        new_iface =Iface(name, ether[name])
        new_iface.fix_ip = ['10.0.' + str(num) + '.1/24']
#        print(new_iface.fix_ip)
        new_iface_dict = {name:{
                            'dhcp4': new_iface.dhcp,
                            'match':{
                                'macaddress': new_iface.hw
                            },
                            'addresses': new_iface.fix_ip}}
        Iface_dict.update(new_iface_dict)
#print(Iface_dict)
#print(plan)

with open("50-cloud-init.yaml", 'w') as f:
    yaml.dump(plan, f)
