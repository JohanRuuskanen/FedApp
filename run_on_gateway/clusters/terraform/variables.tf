variable "cluster_name" {
  default = "example"
}

variable "cloud_name" {
  default = "openstack"
}

variable "az_list" {
  description = "List of Availability Zones available in your OpenStack cluster"
  type        = list
  default     = ["nova"]
}

variable "number_of_k8s_masters" {
  default = 0
}

variable "number_of_k8s_nodes" {
  default = 2
}

variable "number_of_gfs_nodes" {
  default = 0
}

variable "gfs_volume_size_in_gb" {
  default = 75
}

variable "public_key_path" {
  description = "The path of the ssh pub key"
  default     = "~/.ssh/id_rsa.pub"
}

variable "image_name" {
  description = "the image to use"
  default     = "ubuntu-14.04"
}

variable "image_name_gfs" {
  description = "Glance image to use for GlusterFS"
  default     = "ubuntu-16.04"
}

variable "ssh_user" {
  description = "used to fill out tags for ansible inventory"
  default     = "ubuntu"
}

variable "ssh_user_gfs" {
  description = "used to fill out tags for ansible inventory"
  default     = "ubuntu"
}

variable "flavor_name_k8s_masters" {
  description = "Use 'openstack flavor list' command to see what your OpenStack instance flavors"
  default     = 3
}

variable "flavor_name_k8s_nodes" {
  description = "Use 'openstack flavor list' command to see what your OpenStack instance flavors"
  default     = 3
}

variable "flavor_name_gfs_nodes" {
  description = "Use 'openstack flavor list' command to see what your OpenStack instance flavors"
  default     = 3
}

variable "network_name" {
  description = "name of the internal network to use"
  default     = "internal"
}

variable "use_neutron" {
  description = "Use neutron"
  default     = 1
}

variable "subnet_cidr" {
  description = "Subnet CIDR block."
  type        = string
  default     = "10.100.0.0/24"
}

variable "dns_nameservers" {
  description = "An array of DNS name server names used by hosts in this subnet."
  type        = list
  default     = []
}

variable "supplementary_master_groups" {
  description = "supplementary kubespray ansible groups for masters, such kube-node"
  default     = ""
}

variable "supplementary_node_groups" {
  description = "supplementary kubespray ansible groups for worker nodes, such as kube-ingress"
  default     = ""
}

variable "master_allowed_remote_ips" {
  description = "An array of CIDRs allowed to access API of masters"
  type        = list
  default     = ["0.0.0.0/0"]
}

variable "k8s_allowed_remote_ips" {
  description = "An array of CIDRs allowed to SSH to hosts"
  type        = list
  default     = []
}

variable "k8s_allowed_egress_ips" {
  description = "An array of CIDRs allowed for egress traffic"
  type        = list
  default     = ["0.0.0.0/0"]
}

variable "worker_allowed_ports" {
  type = list

  default = [
    {
      "protocol"         = "tcp"
      "port_range_min"   = 30000
      "port_range_max"   = 32767
      "remote_ip_prefix" = "0.0.0.0/0"
    },
  ]
}

variable "gateway_id" {
    default = ""
}

variable "fixed_gw_ip"{
    default = ""
}
