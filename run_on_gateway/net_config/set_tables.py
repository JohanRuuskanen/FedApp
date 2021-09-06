import sys

iface_name_file = sys.argv[1]
with open(iface_name_file, 'r') as f:
    name_list = []
    for line in f:
        name_list.append(line.strip())

with open ('rc.local', 'w') as rsh:
    rsh.write('''\
#!/bin/bash
''')
    rsh.write("sysctl -w net.ipv4.ip_forward=1\n")
    rsh.write("iptables -t nat -A POSTROUTING -o ens3 -j MASQUERADE" + "\n")

    for iface in name_list:
        rsh.write("iptables -A FORWARD -i {} -j ACCEPT\n".format(iface))
        rsh.write("iptables -A FORWARD -o {} -j ACCEPT\n".format(iface))

