import os
import time
import yaml

CLUSTER_ROOT = "/home/ubuntu/run_on_gateway/clusters"
ISTIO_ROOT = "/home/ubuntu/istio-1.9.4"

MESHID = "mesh1"

def create_config(cluster, net):
    f = []
    with open("templates/cluster.yaml", "r") as stream:
        try:
            f = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    f['spec']['values']['global']['meshID'] = MESHID
    f['spec']['values']['global']['network'] = net
    f['spec']['values']['global']['multiCluster']['clusterName'] = cluster

    with open("templates/{}.yaml".format(cluster), "w") as stream:
        try:
            yaml.dump(f, stream, default_flow_style=False)
        except yaml.YAMLError as exc:
            print(exc)

def get_endpoints(clusters):
    eastwest_gw = {}
    for cluster in clusters:
        CMD_getIP = "kubectl --context={} get po -n istio-system".format(cluster) \
            +   " -l istio=eastwestgateway -o jsonpath='{.items[0].status.hostIP}'"
        CMD_getPort = "kubectl --context={} get svc -n istio-system".format(cluster) \
            + " istio-eastwestgateway -o=jsonpath='{.spec.ports[?(@.port==15443)].nodePort}'"
        ip = os.popen(CMD_getIP).read().strip()
        port = os.popen(CMD_getPort).read().strip()
        eastwest_gw[cluster] = (ip, port)

    return eastwest_gw

def gen_meshnetconf(eastwest_gw):
    conf_dict = {}
    
    for cluster in eastwest_gw.keys():
        net = "network-" + cluster.split("-")[-1]
        
        conf_dict[net] = {
            "endpoints": [
                {
                    "fromRegistry": cluster
                }
            ],
            "gateways": [
                {
                    "address": eastwest_gw[cluster][0],
                    "port":  eastwest_gw[cluster][1]
                }
            ]
        }
    return "'networks': " + str(conf_dict)

def patch_meshNetworks(clusters):

    conf = gen_meshnetconf(get_endpoints(clusters))

    for cluster in clusters:

        os.system("kubectl --context={} -n istio-system get configmap/istio".format(cluster) \
            + " -o yaml > templates/istio-configmap-{}.yaml".format(cluster))

        f = []
        with open("templates/istio-configmap-{}.yaml".format(cluster), "r") as stream:
            try:
                f = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        
        f["data"]["meshNetworks"] = conf
        
        with open("templates/istio-configmap-{}.yaml".format(cluster), "w") as stream:
            try:
                yaml.dump(f, stream, default_flow_style=False)
            except yaml.YAMLError as exc:
                print(exc)

        os.system("kubectl --context={} -n istio-system apply".format(cluster) \
            + " -f templates/istio-configmap-{}.yaml".format(cluster))

def deploy_control_plane(clusters):
    
    for cluster in clusters:
        print("====== {} ======\n".format(cluster))

        net = "network-" + cluster.split("-")[-1]

        print("Create istio-system namespace\n")
        os.system("kubectl --context={} create namespace istio-system".format(cluster))

        print("Create k8s secret from CA sertificates\n")
        os.system("kubectl --context={0} create secret generic cacerts -n istio-system \
           --from-file={1}/samples/certs/ca-cert.pem \
           --from-file={1}/samples/certs/ca-key.pem \
           --from-file={1}/samples/certs/root-cert.pem \
           --from-file={1}/samples/certs/cert-chain.pem".format(cluster, ISTIO_ROOT))

        print("Label istio-system namespace\n")
        os.system("kubectl --context={0} label namespace istio-system topology.istio.io/network={1}".format(cluster, net))

        print("Install istio\n")
        create_config(cluster, net)
        os.system("istioctl --context={0} install -y -f templates/{0}.yaml".format(cluster) \
            + " --set hub=gcr.io/istio-release")

        print("Install east-west gateway\n")
        os.system("{0}/samples/multicluster/gen-eastwest-gateway.sh".format(ISTIO_ROOT) \
            + " --mesh {0} --cluster {1} --network {2}".format(MESHID, cluster, net) \
            + " | istioctl --context={0} install -y -f -".format(cluster))

        print("Expose services\n")
        os.system("kubectl --context={} apply -n istio-system".format(cluster) \
            + " -f {}/samples/multicluster/expose-services.yaml".format(ISTIO_ROOT))

        print("")

    print("Adding secrets to remote clusters")
    for cluster in clusters:
        for cluster_remote in clusters:
            if cluster == cluster_remote:
                continue
            os.system("istioctl x create-remote-secret --context={0} --name={0}".format(cluster_remote) \
                + " | kubectl apply -f - --context={}".format(cluster))
    
    print("Patch meshNetworks for working inter-cluster routing")
    patch_meshNetworks(clusters)

    
if __name__ == '__main__':
    clusters = [dir for dir in os.listdir(CLUSTER_ROOT) if "cluster-" in dir]
    clusters.sort()
    deploy_control_plane(clusters)
