#!/usr/bin/env bash

# Add SSH key
eval $(ssh-agent)
ssh-add ~/.ssh/cluster-key

# Install kubernetes
cd $HOME/kubespray
export TFSTATE_ROOT=$1
ansible-playbook -i $1/dynamic_inventory.py --become --become-user=root cluster.yml

# Test if the cluster is reachable
sleep 5
kubectl --kubeconfig=$1/artifacts/admin.conf get nodes
