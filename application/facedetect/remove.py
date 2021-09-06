import os
import settings

# Load the common settings
exec(open("settings.py").read())

if __name__ == '__main__':

    clusters = [dir for dir in os.listdir(ROOT) if "cluster-" in dir]
    clusters.sort()

    files = sorted(filter(lambda x: ".yaml" in x, os.listdir("src")))

    print("Removing the cluster app")
    for cluster in clusters:
        print("====== {} ======".format(cluster))
        os.system("kubectl --context={} -n facedetect delete secret gitlab-auth".format(cluster))
        for file in files:
            os.system("kubectl --context={0} delete -f src/{1}".format(cluster, file))
            

    print("Removing the frontend load balancer")
    os.system("docker rm -f nginx_loadbalancer")
