import os
import time
import subprocess

ROOT = "/home/ubuntu/run_on_gateway/clusters"

def remove_prom_operator(clusters):
    for cluster in clusters:
        print("For %s" % cluster)
        os.system("helm --kube-context=%s --namespace monitoring uninstall po" % cluster)
        os.system("kubectl --context=%s delete crd prometheuses.monitoring.coreos.com" % cluster)
        os.system("kubectl --context=%s delete crd prometheusrules.monitoring.coreos.com" % cluster)
        os.system("kubectl --context=%s delete crd servicemonitors.monitoring.coreos.com" % cluster)
        os.system("kubectl --context=%s delete crd podmonitors.monitoring.coreos.com" % cluster)
        os.system("kubectl --context=%s delete crd probes.monitoring.coreos.com" % cluster)
        os.system("kubectl --context=%s delete crd alertmanagers.monitoring.coreos.com" % cluster)
        os.system("kubectl --context=%s delete crd alertmanagerconfigs.monitoring.coreos.com" % cluster)
        os.system("kubectl --context=%s delete crd thanosrulers.monitoring.coreos.com" % cluster)
        os.system("kubectl --context=%s delete namespace monitoring" % cluster)
        print("\n")

if __name__ == '__main__':
    clusters = [dir for dir in os.listdir(ROOT) if "cluster-" in dir]
    clusters.sort()

    print("Removing the cluster prom-operators")
    remove_prom_operator(clusters)

    print("Removing local grafana")
    os.system("docker rm -f grafana")
    print("\n")
