import os
import subprocess

ROOT = "/home/ubuntu/run_on_gateway/clusters"

def destroy_clusters(clusters):
    for cluster in clusters:
        os.chdir(os.path.join(ROOT, cluster))
        subprocess.run(["terraform", "-chdir=terraform", "destroy", "-auto-approve",
            "-var-file=../gateway.tfvars", 
            "-var-file=../cluster.tfvars"])
        
if __name__ == '__main__':
    clusters = [dir for dir in os.listdir(ROOT) if "cluster-" in dir]
    clusters.sort()
    destroy_clusters(clusters)