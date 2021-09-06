import os

CLUSTER_ROOT = "/home/ubuntu/run_on_gateway/clusters"

def remove_test(clusters):
    for cluster in clusters:
        os.system("kubectl --context={} -n sample delete -f src/sleep.yaml".format(cluster))
        os.system("kubectl --context={} -n sample delete -f src/helloworld.yaml".format(cluster))
        os.system("kubectl --context={} -n sample delete secret gitlab-auth".format(cluster))
        os.system("kubectl --context={} delete namespace sample".format(cluster))

if __name__ == '__main__':
    clusters = [dir for dir in os.listdir(CLUSTER_ROOT) if "cluster-" in dir]
    clusters.sort()
    remove_test(clusters)
