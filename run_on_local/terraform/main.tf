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

resource "openstack_compute_keypair_v2" "create_keypair" {
  name = "${var.keypair_name}"
  public_key = "${file(var.public_key_path)}"
}

resource "openstack_networking_network_v2" "gateway_network" {
  name = "${var.network_name}"
}

resource "openstack_networking_subnet_v2" "gateway_subnet" {
  network_id = "${openstack_networking_network_v2.gateway_network.id}"
  cidr       = "${var.subnet_cidr}"
  ip_version = 4
}

resource "openstack_networking_router_v2" "gateway_router" {
  name = "${var.router_name}"
  external_network_id  = "${var.external_network_id}"
}

resource "openstack_networking_router_interface_v2" "router_interface_1" {
  router_id = "${openstack_networking_router_v2.gateway_router.id}"
  subnet_id = "${openstack_networking_subnet_v2.gateway_subnet.id}"
}


resource "openstack_networking_secgroup_v2" "gateway_secgroup" {
  name        = "${var.gateway_name}-secgroup_gateway_ssh"
  description = "ssh"
}

resource "openstack_networking_secgroup_rule_v2" "ssh_rule" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = "${openstack_networking_secgroup_v2.gateway_secgroup.id}"
}

resource "openstack_networking_secgroup_rule_v2" "icmp_rule" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "icmp"
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = "${openstack_networking_secgroup_v2.gateway_secgroup.id}"
}

resource "openstack_compute_instance_v2" "gateway_instance" {
  name            = "${var.gateway_name}"
  image_name        = "${var.gateway_image}"
  flavor_name     = "${var.gateway_flavor_name}"
  key_pair        = "${openstack_compute_keypair_v2.create_keypair.name}"
  security_groups = ["${openstack_networking_secgroup_v2.gateway_secgroup.name}"]

  network {
    uuid = "${openstack_networking_subnet_v2.gateway_subnet.network_id}"
  }

  metadata = {
    ssh_user = "${var.ssh_user}"
  }
  
}

resource "openstack_networking_floatingip_v2" "gateway_floating_ip" {
  pool = "internet"
}

resource "openstack_compute_floatingip_associate_v2" "associate_ip" {
  floating_ip = "${openstack_networking_floatingip_v2.gateway_floating_ip.address}"
  instance_id = "${openstack_compute_instance_v2.gateway_instance.id}"
}

output "ip_address" {
  value = "${openstack_networking_floatingip_v2.gateway_floating_ip.address}"
}

resource "local_file" "ansible_host_file" {
    content     = templatefile("${path.module}/hosts.tmpl", { ip = "${openstack_networking_floatingip_v2.gateway_floating_ip.address}" })
    filename = "${path.module}/../ansible/inventory/gateway"
}

resource "local_file" "gateway_file" {
    content     = templatefile("${path.module}/gateway.tmpl", { id = "${openstack_compute_instance_v2.gateway_instance.id}" })
    filename = "${path.module}/../gateway.tfvars"
}
