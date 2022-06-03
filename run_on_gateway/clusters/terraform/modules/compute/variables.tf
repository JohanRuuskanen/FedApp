variable "cluster_name" {}

variable "cloud_name" {}

variable "az_list" {
  type = list
}

variable "number_of_k8s_masters" {}

variable "number_of_k8s_nodes" {}

variable "number_of_gfs_nodes" {}

variable "gfs_volume_size_in_gb" {}

variable "public_key_path" {}

variable "image_name" {}

variable "image_name_gfs" {}

variable "ssh_user" {}

variable "ssh_user_gfs" {}

variable "flavor_name_k8s_master" {}

variable "flavor_name_k8s_node" {}

variable "flavor_name_gfs_node" {}

variable "network_name" {}

variable "network_id" {
  default = ""
}
variable "subnet_id" {
  default = ""
}

variable "master_allowed_remote_ips" {
  type = list
}

variable "k8s_allowed_remote_ips" {
  type = list
}

variable "k8s_allowed_egress_ips" {
  type = list
}

variable "supplementary_master_groups" {
  default = ""
}

variable "supplementary_node_groups" {
  default = ""
}

variable "worker_allowed_ports" {
  type = list
}
