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

module "network" {
  source = "./modules/network"

  cloud_name      = "${var.cloud_name}"
  network_name    = "${var.network_name}"
  subnet_cidr     = "${var.subnet_cidr}"
  cluster_name    = "${var.cluster_name}"
  dns_nameservers = "${var.dns_nameservers}"
  use_neutron     = "${var.use_neutron}"
  fixed_ip        = "${var.fixed_gw_ip}"
}

module "compute" {
  source = "./modules/compute"

  cloud_name                                   = "${var.cloud_name}"
  cluster_name                                 = "${var.cluster_name}"
  az_list                                      = "${var.az_list}"
  number_of_k8s_masters                        = "${var.number_of_k8s_masters}"
  number_of_k8s_nodes                          = "${var.number_of_k8s_nodes}"
  number_of_gfs_nodes                          = "${var.number_of_gfs_nodes}"
  gfs_volume_size_in_gb                        = "${var.gfs_volume_size_in_gb}"
  public_key_path                              = "${var.public_key_path}"
  image_name                                   = "${var.image_name}"
  image_name_gfs                               = "${var.image_name_gfs}"
  ssh_user                                     = "${var.ssh_user}"
  ssh_user_gfs                                 = "${var.ssh_user_gfs}"
  flavor_name_k8s_master                         = "${var.flavor_name_k8s_masters}"
  flavor_name_k8s_node                           = "${var.flavor_name_k8s_nodes}"
  flavor_name_gfs_node                           = "${var.flavor_name_gfs_nodes}"
  network_name                                 = "${var.network_name}"
  master_allowed_remote_ips                    = "${var.master_allowed_remote_ips}"
  k8s_allowed_remote_ips                       = "${var.k8s_allowed_remote_ips}"
  k8s_allowed_egress_ips                       = "${var.k8s_allowed_egress_ips}"
  supplementary_master_groups                  = "${var.supplementary_master_groups}"
  supplementary_node_groups                    = "${var.supplementary_node_groups}"
  worker_allowed_ports                         = "${var.worker_allowed_ports}"

  network_id                                   = "${module.network.network_id}"
  subnet_id                                    = "${module.network.subnet_id}"
}

module "gateway" {
  source = "./modules/gateway"

  cloud_name    = "${var.cloud_name}"
  gateway_id    = "${var.gateway_id}"
  network_port  = "${module.network.network_port_id}"

}

output "private_subnet_id" {
  value = "${module.network.subnet_id}"
}
