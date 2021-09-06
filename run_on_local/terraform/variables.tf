
variable "network_name" {
  description = "name of the internal network to use"
  default     = "gateway-network"
}

variable "router_name" {
  description = "name of the external facing router"
  default = "gateway-router"
}

variable "gateway_name" {
  description = "name of the gateway VM"
  default = "gateway"
}

variable "keypair_name" {
  description = "name of the keypair"
  default = "keypair"
}

variable "public_key_path" {
  description = "The path of the ssh pub key"
  default     = "~/.ssh/id_rsa.pub"
}

variable "ssh_user" {
  description = "The SSH user"
  default = "ubuntu"
}

variable "gateway_image" {
  description = "Image name of the gateway virtual machine"
  default = ""
}

variable "gateway_flavor_id" {
  description = "The amount of vCPUs and RAM to assign the gateway virtual machine"
  default = ""
}

variable "external_network_id" {
  description = "ID of the external network"
  default = ""
}

variable "cloud_name" {
  description = "name of the cloud in clouds.yaml"
  default = "openstack"
}

variable "subnet_cidr" {
  description = "Subnet CIDR block."
  type        = string
  default     = "10.0.0.0/24"
}
