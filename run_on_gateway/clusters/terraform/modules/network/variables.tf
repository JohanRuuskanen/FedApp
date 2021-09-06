variable "cloud_name" {}

variable "network_name" {}

variable "cluster_name" {}

variable "dns_nameservers" {
  type = list
}

variable "subnet_cidr" {}

variable "use_neutron" {}

variable "fixed_ip" {}
