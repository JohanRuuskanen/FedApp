
import os
import yaml

CLUSTER_1 = "cluster-1"
CLUSTER_2 = "cluster-2"

CLUSTER_ROOT = "/home/ubuntu/run_on_gateway/clusters"

def deploy_test(clusters):

    for cluster in clusters:
        print("====== {} ======".format(cluster))

        os.system("kubectl --context={} create namespace sample".format(cluster))
        os.system("kubectl --context={} label namespace sample istio-injection=enabled".format(cluster))
        os.system("kubectl --context={} -n sample create secret generic gitlab-auth".format(cluster) \
            + " --from-file=.dockerconfigjson=/home/ubuntu/.docker/config.json" \
            + " --type=kubernetes.io/dockerconfigjson")

        os.system("kubectl --context={} apply -n sample -f src/helloworld.yaml".format(cluster))
        os.system("kubectl --context={} apply -n sample -f src/sleep.yaml".format(cluster))

if __name__ == '__main__':
    clusters = [dir for dir in os.listdir(CLUSTER_ROOT) if "cluster-" in dir]
    clusters.sort()
    deploy_test(clusters)
