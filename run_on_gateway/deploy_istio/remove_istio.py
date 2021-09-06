import os

CLUSTER_ROOT = "/home/ubuntu/run_on_gateway/clusters"

def remove_istio(clusters):
    for cluster in clusters:
        os.system("istioctl --context={0} x uninstall --purge -y".format(cluster))
        os.system("kubectl --context={0} delete namespace istio-system".format(cluster))


if __name__ == '__main__':
    clusters = [dir for dir in os.listdir(CLUSTER_ROOT) if "cluster-" in dir]
    clusters.sort()
    remove_istio(clusters)

