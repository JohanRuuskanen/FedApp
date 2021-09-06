output "subnet_id" {
  value = "${element(concat(openstack_networking_subnet_v2.k8s.*.id, tolist([""])), 0)}"
}

output "network_id" {
  value = "${element(concat(openstack_networking_network_v2.k8s.*.id, tolist([""])), 0)}"
}
output "network_port_id" {
  value = "${element(concat(openstack_networking_port_v2.k8s.*.id, tolist([""])), 0)}"
}