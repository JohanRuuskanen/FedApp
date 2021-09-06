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

resource "openstack_networking_network_v2" "k8s" {
  name           = "${var.network_name}"
  count          = "${var.use_neutron}"
  admin_state_up = "true"
}

resource "openstack_networking_subnet_v2" "k8s" {
  name            = "${var.cluster_name}-internal-network"
  count           = "${var.use_neutron}"
  network_id      = "${openstack_networking_network_v2.k8s[count.index].id}"
  cidr            = "${var.subnet_cidr}"
  ip_version      = 4
  dns_nameservers = "${var.dns_nameservers}"
}

resource "openstack_networking_port_v2" "k8s" {
  name           = "${var.cluster_name}-network-port"
  count           = "${var.use_neutron}"
  network_id     = "${openstack_networking_network_v2.k8s[count.index].id}"
  admin_state_up = "true"
  port_security_enabled = false

  fixed_ip {
    subnet_id = "${openstack_networking_subnet_v2.k8s[count.index].id}"
    ip_address = "${var.fixed_ip}"
  }

}
