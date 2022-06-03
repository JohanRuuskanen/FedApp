terraform {
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.17"
    }
  }
}

provider "openstack" {
  cloud = "${var.cloud_name}"
}

resource "openstack_compute_keypair_v2" "k8s" {
  name       = "kubernetes-${var.cluster_name}"
  public_key = "${chomp(file(var.public_key_path))}"
}

resource "openstack_networking_secgroup_v2" "k8s_master" {
  name                 = "${var.cluster_name}-k8s-master"
  description          = "${var.cluster_name} - Kubernetes Master"
  delete_default_rules = true
}

resource "openstack_networking_secgroup_rule_v2" "k8s_master" {
    count             = "${length(var.master_allowed_remote_ips)}"
    direction         = "ingress"
    ethertype         = "IPv4"
    protocol          = "tcp"
    port_range_min    = "6443"
    port_range_max    = "6443"
    remote_ip_prefix  = "${var.master_allowed_remote_ips[count.index]}"
    security_group_id = "${openstack_networking_secgroup_v2.k8s_master.id}"
}

resource "openstack_networking_secgroup_rule_v2" "k8s_master_ssh" {
    count             = "${length(var.master_allowed_remote_ips)}"
    direction         = "ingress"
    ethertype         = "IPv4"
    protocol          = "tcp"
    port_range_min    = "22"
    port_range_max    = "22"
    remote_ip_prefix  = "${var.master_allowed_remote_ips[count.index]}"
    security_group_id = "${openstack_networking_secgroup_v2.k8s_master.id}"
}

resource "openstack_networking_secgroup_rule_v2" "k8s_master_icmp" {
    count             = "${length(var.master_allowed_remote_ips)}"
    direction         = "ingress"
    ethertype         = "IPv4"
    protocol          = "icmp"
    remote_ip_prefix  = "${var.master_allowed_remote_ips[count.index]}"
    security_group_id = "${openstack_networking_secgroup_v2.k8s_master.id}"
}

resource "openstack_networking_secgroup_v2" "k8s" {
  name                 = "${var.cluster_name}-k8s"
  description          = "${var.cluster_name} - Kubernetes"
  delete_default_rules = true
}

resource "openstack_networking_secgroup_rule_v2" "k8s" {
  direction         = "ingress"
  ethertype         = "IPv4"
  remote_group_id   = "${openstack_networking_secgroup_v2.k8s.id}"
  security_group_id = "${openstack_networking_secgroup_v2.k8s.id}"
}

resource "openstack_networking_secgroup_rule_v2" "k8s_allowed_remote_ips" {
  count             = "${length(var.k8s_allowed_remote_ips)}"
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = "22"
  port_range_max    = "22"
  remote_ip_prefix  = "${var.k8s_allowed_remote_ips[count.index]}"
  security_group_id = "${openstack_networking_secgroup_v2.k8s.id}"
}

resource "openstack_networking_secgroup_rule_v2" "egress" {
  count             = "${length(var.k8s_allowed_egress_ips)}"
  direction         = "egress"
  ethertype         = "IPv4"
  remote_ip_prefix  = "${var.k8s_allowed_egress_ips[count.index]}"
  security_group_id = "${openstack_networking_secgroup_v2.k8s.id}"
}

resource "openstack_networking_secgroup_v2" "worker" {
  name                 = "${var.cluster_name}-k8s-worker"
  description          = "${var.cluster_name} - Kubernetes worker nodes"
  delete_default_rules = true
}

resource "openstack_networking_secgroup_rule_v2" "worker" {
  count             = "${length(var.worker_allowed_ports)}"
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "${lookup(var.worker_allowed_ports[count.index], "protocol", "tcp")}"
  port_range_min    = "${lookup(var.worker_allowed_ports[count.index], "port_range_min")}"
  port_range_max    = "${lookup(var.worker_allowed_ports[count.index], "port_range_max")}"
  remote_ip_prefix  = "${lookup(var.worker_allowed_ports[count.index], "remote_ip_prefix", "0.0.0.0/0")}"
  security_group_id = "${openstack_networking_secgroup_v2.worker.id}"
}

resource "openstack_networking_secgroup_rule_v2" "worker_ssh" {
  count             = "${length(var.worker_allowed_ports)}"
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = "22"
  port_range_max    = "22"
  remote_ip_prefix  = "${lookup(var.worker_allowed_ports[count.index], "remote_ip_prefix", "0.0.0.0/0")}"
  security_group_id = "${openstack_networking_secgroup_v2.worker.id}"
}

resource "openstack_networking_port_v2" "master_port" {
  name           = "${count.index + 1}-master-port"
  count          = "${var.number_of_k8s_masters}"
  network_id     = "${var.network_id}"
  admin_state_up = "true"
  port_security_enabled = false

  fixed_ip {
    subnet_id = "${var.subnet_id}"
  }
}

resource "openstack_compute_instance_v2" "k8s_master" {
  name              = "${var.cluster_name}-k8s-master-nf-${count.index+1}"
  count             = "${var.number_of_k8s_masters}"
  availability_zone = "${element(var.az_list, count.index)}"
  image_name        = "${var.image_name}"
  flavor_name         = "${var.flavor_name_k8s_master}"
  key_pair          = "${openstack_compute_keypair_v2.k8s.name}"

  network {
    port = "${openstack_networking_port_v2.master_port[count.index].id}"
  }

  metadata = {
    ssh_user         = "${var.ssh_user}"
    kubespray_groups = "etcd,kube-master,${var.supplementary_master_groups},k8s-cluster,vault,no-floating"
    depends_on       = "${var.subnet_id}"
  }
}

resource "openstack_networking_port_v2" "node_port" {
  name           = "${count.index + 1}-node-port"
  count          = "${var.number_of_k8s_nodes}"
  network_id     = "${var.network_id}"
  admin_state_up = "true"
  port_security_enabled = false

  fixed_ip {
    subnet_id = "${var.subnet_id}"
  }
}
resource "openstack_compute_instance_v2" "k8s_node" {
  name              = "${var.cluster_name}-k8s-node-nf-${count.index+1}"
  count             = "${var.number_of_k8s_nodes}"
  availability_zone = "${element(var.az_list, count.index)}"
  image_name        = "${var.image_name}"
  flavor_name         = "${var.flavor_name_k8s_node}"
  key_pair          = "${openstack_compute_keypair_v2.k8s.name}"

  network {
    port = "${openstack_networking_port_v2.node_port[count.index].id}"
  }

  metadata = {
    ssh_user         = "${var.ssh_user}"
    kubespray_groups = "kube-node,k8s-cluster,no-floating,${var.supplementary_node_groups}"
    depends_on       = "${var.subnet_id}"
  }
}

resource "openstack_blockstorage_volume_v2" "glusterfs_volume" {
  name        = "${var.cluster_name}-glusterfs_volume-${count.index+1}"
  count       = "${var.number_of_gfs_nodes}"
  description = "Non-ephemeral volume for GlusterFS"
  size        = "${var.gfs_volume_size_in_gb}"
}

resource "openstack_compute_instance_v2" "glusterfs_node" {
  name              = "${var.cluster_name}-gfs-node-nf-${count.index+1}"
  count             = "${var.number_of_gfs_nodes}"
  availability_zone = "${element(var.az_list, count.index)}"
  image_name        = "${var.image_name_gfs}"
  flavor_name         = "${var.flavor_name_gfs_node}"
  key_pair          = "${openstack_compute_keypair_v2.k8s.name}"

  network {
    name = "${var.network_name}"
  }

  security_groups = ["${openstack_networking_secgroup_v2.k8s.name}"]

  metadata = {
    ssh_user         = "${var.ssh_user_gfs}"
    kubespray_groups = "gfs-cluster,network-storage,no-floating"
  }
}

resource "openstack_compute_volume_attach_v2" "glusterfs_volume" {
  count       = "${var.number_of_gfs_nodes}"
  instance_id = "${element(openstack_compute_instance_v2.glusterfs_node.*.id, count.index)}"
  volume_id   = "${element(openstack_blockstorage_volume_v2.glusterfs_volume.*.id, count.index)}"
}
