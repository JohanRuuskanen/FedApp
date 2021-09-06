import sys
import os
import shutil
import argparse
import numpy as np
import subprocess
import csv

DELAY_MATRIX = "/home/ubuntu/run_on_gateway/chaos_netem/matrix.csv"

def read_map(networks):
    dim = len(networks)
    default_matrix = np.zeros((dim, dim))
    delay_matrix = []
    try:
        with open(DELAY_MATRIX, "r") as file:
            reader = csv.reader(file, quoting=csv.QUOTE_NONNUMERIC) # change contents to floats
            for row in reader: # each row is a list
                delay_matrix.append(row)
            delay_matrix = np.array(delay_matrix)
            if np.shape(delay_matrix) != np.shape(default_matrix):
                print("Wrong matrix dimension, use defualt")
                delay_matrix = default_matrix
            for i in range(dim):
                if delay_matrix[i][i] != 0:
                    print("Wrong matrix, use defualt")
                    delay_matrix = default_matrix
                    break
    except FileNotFoundError:
        print("No delay matrix found, use default")
        delay_matrix = default_matrix

    return delay_matrix

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('networks', metavar='N', nargs='+',
                    help='net work lists')

    args = parser.parse_args()
    networks = args.networks

    # Filter out networks not related to the clusters, e.g. docker0. This could be
    # made smarter if filtering on the IP's instead, to only choose networks with
    # IP's 10.0.i.0 where i > 0
    networks = [n for n in networks if n.find("ens") == 0 and n != "ens3"]

    matrix = read_map(networks)

    # Restore
    print("If old config exist, restore to default first")
    for dst in range(len(networks)):
        subprocess.run(["tc", "qdisc", "del", "dev", networks[dst], "root"])

    for dst in range(len(networks)):
        subprocess.run(["tc", "qdisc", "add", "dev", networks[dst], "handle", "1:", "root", "htb", "r2q", "1700"])
        subprocess.run(["tc", "class", "add", "dev", networks[dst], "parent", "1:", "classid", "1:1", "htb", "rate", "10Gbps", "ceil", "10Gbps"])
        flow = 11
        for src in range(len(networks)):
            if matrix[src][dst] == 0:
                pass
            else:
                src_address = "10.0."+str(src+1)+".0/24"
                delay = str(matrix[src][dst]) + "ms"
                print("Add delay of {} from {} ({}) to {}".format(delay, networks[src], src_address, networks[dst]))
                classid = "1:"+str(flow)
                handle_nbr = str((flow-10)*10)+":"
                subprocess.run(["tc", "class", "add", "dev", networks[dst], "parent", "1:1", "classid", classid, "htb", "rate", "10Gbps"])
                subprocess.run(["tc", "qdisc", "add", "dev", networks[dst], "parent", classid, "handle", handle_nbr, "netem", "delay", delay])
                subprocess.run(["tc", "filter", "add", "dev", networks[dst], "parent", "1:", "protocol", 'ip', "prio", "1", "u32", "match", "ip", "src", src_address, "flowid", classid])
                flow += 1
