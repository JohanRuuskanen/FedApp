import os
import time
import yaml
import json
import subprocess

ROOT = "/home/ubuntu/run_on_gateway/clusters"

def deploy_monitoring(clusters):
    for cluster in clusters:

        print("====== {} ======".format(cluster))

        os.system("kubectl --context=%s create ns monitoring" % cluster)

        log = open('logs/deploy-%s.log' % cluster, "w")

        CMD = ["helm", "--kube-context=%s" % cluster, "install",
                "po", "--namespace=monitoring",
                "prometheus-community/kube-prometheus-stack",
                "-f", "misc/values.yaml",
                "--version", "15.4.4"]

        proc = subprocess.Popen(CMD, stdout=log, stderr=log, shell=False)

        proc.wait()
        log.close()
        print("\t {} monitor deployment completed".format(cluster))

def retrieve_cluster_IPs(clusters):
    ips = {}
    for (i, cluster) in enumerate(clusters):
        CMD = "kubectl --context=%s get nodes -o wide | grep master | awk '{print $6}'" % cluster
        masterip = os.popen(CMD).read().strip()
        ips[cluster] = masterip

    return ips

def generate_datasources(clusters):
    if not os.path.isdir("grafana/datasources"):
        os.makedirs("grafana/datasources")

    ips = retrieve_cluster_IPs(clusters)

    D = {"datasources": []}
    for cluster in clusters:
        d = {   "name": cluster,
                "url": "http://" + ips[cluster] + ":30090",
                "type": "prometheus",
                "access": "proxy"
             }
        D["datasources"].append(d)

    with open("grafana/datasources/datasources.yaml", "w") as f:
        try:
            yaml.dump(D, f, default_flow_style=False)
        except yaml.YAMLError as exc:
            print(exc)

def generate_fed_monitoring_dashboard(clusters):
    if not os.path.isdir("grafana/dashboards"):
        os.makedirs("grafana/dashboards")

    with open("misc/fed_dashboard.tmpl", "r") as tmpl_file:
        json_data = json.load(tmpl_file)

    char_list = [chr(i) for i in range(ord("A"), ord("A") + len(clusters))]
    nbr_panels = len(json_data['panels'])

    for k in range(nbr_panels):
        tmpl = json_data['panels'][k]['targets'][0]
        json_data['panels'][k]['targets'] = []
        for (i, cluster) in enumerate(clusters):
            c = tmpl.copy()
            c['datasource'] = cluster
            c['legendFormat'] = cluster
            c['refId'] = char_list[i]
            json_data['panels'][k]['targets'].append(c)

    with open("grafana/fed_dashboard.json", "w") as json_file:
        json.dump(json_data, json_file, indent=2, sort_keys=True)

def launch_grafana():
    # Build image ontop of grafana with the new provisioning
    os.system("docker build -t grafana-add_prov grafana/")

    # Launch the container
    os.system("docker run -d -p 3000:3000 --name=grafana grafana-add_prov")


if __name__ == '__main__':
    if not os.path.isdir("logs"):
        os.mkdir("logs")

    clusters = [dir for dir in os.listdir(ROOT) if "cluster-" in dir]
    clusters.sort()

    print("Add the kube-prometheus-stack chart")
    os.system("helm repo add prometheus-community https://prometheus-community.github.io/helm-charts")
    os.system("helm repo update")

    print("Launching the prometheus-operator on all clusters")
    deploy_monitoring(clusters)
    print("\n")

    print("Launching local grafana")
    generate_datasources(clusters)
    generate_fed_monitoring_dashboard(clusters)
    launch_grafana()
    print("\n")
