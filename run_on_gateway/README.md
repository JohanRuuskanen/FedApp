## Setup the cluster software stacks

To setup the sandbox clusters, do the following steps in order. All the steps are run on the Gateway VM.

### For the virtual clusters
The virtualized infrastructure for the clusters is created from the  `run_on_gateway/create_clusters` folder.

- First add the OpenStack authentification to the Gateway VM. If authentication is handled by the`~/.config/openstack/clouds.yml` file , it will have been copied automatically when setting up the gateway.
- Copy the file `cluster.tmpl` to form a `.tfvar` file for each cluster that should be created. Name the files `cluster-x.tfvars` where x is an ascending integer starting from 1. 
- Change the variables in each `create_clusters/cluster-x.tfvars` to your liking. The things required to change are the 
- * The name of the cluster/network
  * The subnet CIDR and gateway IP of the cluster local network
  * The flavor IDs of the virtual machines in the clusters
- To then create the clusters, run `python3 create_clusters.py`. To delete the clusters, run `python3 destroy_clusters.py`

### For the network configuration

To setup the internal cluster-to-cluster and cluster-to-internet networking, visit `run_on_gateway/net_config` and simply run `sudo sh set_gw.sh`.  Wait until the machine is restarted, then test if you can access the machines by first adding the cluster SSH key

```bash
eval $(ssh-agent -s)
ssh-add /home/ubuntu/.ssh/cluster-key
```

and then connecting to a VM in a cluster via SSH. 

### For Kubernetes

To setup Kubernetes on all clusters, simply visit `run_on_gateway/deploy_kubernetes` and run

```bash
python3 deploy_kubernetes.py
```

If something goes wrong, the installation stores kubespray's stdout in the logs directory.

After installation, all cluster configs are merged and put into `~/.kube/config`. To run a command on cluster-x simply type

```bash
kubectl --context=cluster-x COMMAND
```

### For federation-wide Prometheus/Grafana
To deploy federation-wide monitoring, visit `fed_monitoring` and run

```bash
python3 deploy_monitoring.py
```

If the installation from prom-operator fails, the stdout/stderr are saved in `logs/deploy-cluster-i.log`. To check the installation status on cluster-i run

```bash
kubectl --context=cluster-i get pods -n monitoring
```

To access Grafana, port forwarding using SSH from your local computer to the gateway can be used with

```bash
ssh -L 3000:localhost:3000 ubuntu@GATEWAY-IP
```

Grafana can now be accessed at `http://localhost:3000` at your local computer. The default username/password is admin/admin.

The deployment can be removed with

```bash
python3 remove_deployment.py
```

### For Istio

To setup istio with a multi-cluster service mesh across all clusters, visit `deploy_istio` and run

```bash
python3 deploy_istio
```

To uninstall install istio, simply run

```bash
python3 remove_istio.py
```

In `deploy_istio/validate` there are scripts for launching a simple service for validation. First, the `helloworld` service needs to be built and pushed to some container registry. For this we have assumed a registry hosted on gitlab, but other registries should work with low effort.

First update the `src/build_and_push.sh` and `helloworld.yaml` files to supply the correct paths to the registry/image, and then run

```bash
chmod +x build_and_push.sh
./build_and_push.sh
```

Then deploy the validation example with

```bash
python3 deploy_test.py
```

After the containers have successfully started, run

```
sh runtest.sh cluster-1
```

to e.g. test the connection from a service in cluster-1 to the `helloworld` services running in the other clusters. 

To remove the validation example, simply run

```
python3 remove_test.py
```

### Adding network characteristics via Netem

To add inter-cluster network characteristics, visit the `run_on_gateway/netem` folder.

* To add delay on an entire network interface between the Gateway VM and a cluster, run e.g.

```bash
sudo tc qdisc add dev ens9 root netem delay 100ms
```

* To instead add e.g. loss rate (once you added an initial characteristic, you can just use `change` for it)

```bash
sudo tc qdisc change dev ens9 root netem loss 0.1%
```

TC-netem has a whole array of different network characteristics that can be introduced, see e.g. https://wiki.linuxfoundation.org/networking/netem.

We have supplied a script that can make this easier. Simply run

```bash
sudo ./start.sh
```

and choose an option. This script simplifies the work needed to add cluster-to-cluster characteristics  that does not affect the gateway-to-cluster connection. 

At the moment, you can out-of-the-box add delays by changing in the `matrix.csv` file and running option 5). It is important that the size is NxN where N is the amount of allocated clusters. 

To add another network characteristic than delay between clusters, simply change the line 69 in `network_mapping.py` that adds delay to a filtered connection.  