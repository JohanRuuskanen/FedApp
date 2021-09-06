
import os
import yaml
import time
import subprocess

ROOT = "/home/ubuntu/run_on_gateway/clusters"

def deploy_kubernetes(clusters):

    subprocess.run(["chmod", "+x", "k8s_script.sh"])

    for cluster in clusters:
        time.sleep(5)

        print("{} started".format(cluster))

        root_path = '/home/ubuntu/run_on_gateway/clusters/%s' % cluster

        log = open('logs/%s.log' % cluster, "w")
        proc = subprocess.Popen(["./k8s_script.sh", root_path, cluster],
            stdout=log, shell=False)

        # At the moment, the installation is done in serial but could
        # potentially be done in parallel. Care needs to be taken then
        # since too many simultaneously running instances might break
        # the installation
        proc.wait()
        log.close()
        print("{} completed".format(cluster))

def merge_configs(clusters):

    # Rename clusters, contexts and users
    print("Rewriting YAML config files")
    for cluster in clusters:
        root_path = '/home/ubuntu/run_on_gateway/clusters/%s' % cluster
        f = []
        with open(root_path + "/artifacts/admin.conf", "r") as stream:
            try:
                f = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        f['clusters'][0]['name'] = cluster
        f['users'][0]['name'] = cluster + "-admin"

        f['contexts'][0]['context']['cluster'] = f['clusters'][0]['name']
        f['contexts'][0]['context']['user'] = f['users'][0]['name']

        f['contexts'][0]['name'] = cluster
        f['current-context'] = cluster

        with open(root_path + "/artifacts/admin_renamed.conf", "w") as stream:
            try:
                yaml.dump(f, stream, default_flow_style=False)
            except yaml.YAMLError as exc:
                print(exc)

    # Merge and export config file to ~/.kube/config
    print("Merging config files")
    config_files = [ROOT + "/" + cluster + "/artifacts/admin_renamed.conf" for cluster in clusters]
    merge_files = ":".join(config_files)
    os.system("KUBECONFIG=%s kubectl config view --merge --flatten > ~/.kube/config" \
        % merge_files)

def test_clusters(clusters):
    for cluster in clusters:
        print("Testing {}".format(cluster))
        os.system("kubectl --context=%s get nodes" % cluster)

if __name__ == '__main__':
    if not os.path.isdir("logs"):
        os.mkdir("logs")

    clusters = [dir for dir in os.listdir(ROOT) if "cluster-" in dir]
    clusters.sort()
    
    deploy_kubernetes(clusters)
    merge_configs(clusters)
    test_clusters(clusters)
