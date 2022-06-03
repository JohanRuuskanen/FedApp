import os
import yaml
import time

# Load the common settings
exec(open("settings.py").read())

def deploy(clusters):
    for cluster in clusters:
        print("====== {} ======".format(cluster))
        if not ((cluster in FRONTEND_CLUSTERS) or (cluster in BACKEND_CLUSTERS)):
            continue
        os.system("kubectl --context={} apply -f src/namespace.yaml".format(cluster))
        os.system("kubectl --context={} -n facedetect create secret generic gitlab-auth".format(cluster) \
            + " --from-file=.dockerconfigjson=/home/ubuntu/.docker/config.json" \
            + " --type=kubernetes.io/dockerconfigjson")

        os.system("kubectl --context={} apply -f src/backend.yaml -l service=backend".format(cluster))

def deploy_frontend():
    for frontend_cluster in FRONTEND_CLUSTERS:
        print("====== {} ======".format(frontend_cluster))
        os.system("kubectl --context={} apply -f src/frontend.yaml".format(frontend_cluster))

def deploy_backend():
    for backend_cluster in BACKEND_CLUSTERS:
        print("====== {} ======".format(backend_cluster))
        os.system("kubectl --context={} apply -f src/backend.yaml".format(backend_cluster))

def retrieve_cluster_IPs(clusters):
    ips = {}
    for (i, cluster) in enumerate(clusters):
        CMD = "kubectl --context=%s get nodes -o wide | grep master | awk '{print $6}'" % cluster
        masterip = os.popen(CMD).read().strip()
        ips[cluster] = masterip
    return ips

def generate_nginxconf(clusters):

    ips = retrieve_cluster_IPs(clusters)

    us_api = ""
    for frontend_cluster in FRONTEND_CLUSTERS:
        us_api += "server %s:31111;\n" % ips[frontend_cluster]

    conf = """
    user    nginx;
    worker_processes        1;
    error_log  /var/log/nginx/error.log warn;
    pid        /var/run/nginx.pid;

    events {
            worker_connections      1024;
    }
    http {
            proxy_http_version 1.1;

            client_max_body_size 12M;
            upstream api {
                %s
            }

            server {
                    listen 3001;

                    location / {
                            proxy_pass http://api/;
                    }
            }
    }
    """ % (us_api)

    with open("nginx.conf", "w") as f:
        f.write(conf)


def launch_nginx():
    os.system("docker run -d  --network=host \
        -v /home/ubuntu/application/facedetect/nginx.conf:/etc/nginx/nginx.conf:ro \
        --name=nginx_loadbalancer nginx:1.17.10")

if __name__ == '__main__':

    clusters = [dir for dir in os.listdir(ROOT) if "cluster-" in dir]
    clusters.sort()

    deploy(clusters)
    deploy_frontend()
    deploy_backend()
    generate_nginxconf(clusters)
    launch_nginx()
