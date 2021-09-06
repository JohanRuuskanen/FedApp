#!/bin/bash

# On the GW, set up interfaces and routing as well
cp /etc/netplan/50-cloud-init.yaml .
cp 50-cloud-init.yaml backup_50-cloud-init.yaml

ifconfig -a -s | awk '($1 !="Iface" && $1 != "lo" && $1 != "docker0") {print $1}' > name.txt
python3 set_plan.py name.txt

cp 50-cloud-init.yaml /etc/netplan/50-cloud-init.yaml

netplan generate
netplan apply

echo "Set netplan done!"

python3 set_tables.py name.txt
cp rc.local /etc/.
chmod 755 /etc/rc.local

echo "Set ipatbles done!"

rm name.txt
rm -f 50-cloud-init.yaml
rm -f rc.local

echo "Restart the machine to enable the setups"

sleep 3
reboot
