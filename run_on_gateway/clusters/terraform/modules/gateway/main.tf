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

resource "openstack_compute_interface_attach_v2" "connect_to_gateway" {
  instance_id = "${var.gateway_id}"
  port_id = "${var.network_port}"
}
