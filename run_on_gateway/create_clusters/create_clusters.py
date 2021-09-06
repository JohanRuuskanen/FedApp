import os
import subprocess
import time

ROOT = '/home/ubuntu/run_on_gateway'

def create_clusters(clusters):
    for cluster in clusters:

        cluster_folder = os.path.join(ROOT, "clusters", cluster.split(".")[0])
        if not os.path.isdir(cluster_folder):
            os.mkdir(cluster_folder)
        os.chdir(cluster_folder)

        subprocess.run(["cp", os.path.join(ROOT, "create_clusters", "gateway.tfvars"), "."])
        subprocess.run(["cp", os.path.join(ROOT, "create_clusters", cluster), "cluster.tfvars"])
        subprocess.run(["cp", "-r", "../terraform", "."])
        subprocess.run(["cp", "../dynamic_inventory.py", "."])
        subprocess.run(["chmod", "+x", "dynamic_inventory.py"])
        subprocess.run(["cp", "-r", "../group_vars", "."])
        subprocess.run(["terraform", "-chdir=terraform", "init"])

        terraform_install_cmd = ["terraform", "-chdir=terraform", "apply", "-auto-approve", 
            "-var-file=../gateway.tfvars", 
            "-var-file=../cluster.tfvars"]
        resTer = subprocess.run(terraform_install_cmd)
        if resTer.returncode != 0:
            time.sleep(10)
            resTer = subprocess.run(terraform_install_cmd)

if __name__ == '__main__':
    clusters = [dir for dir in os.listdir(os.path.join(ROOT, "create_clusters")) if "cluster-" in dir]
    clusters.sort()
    create_clusters(clusters)
