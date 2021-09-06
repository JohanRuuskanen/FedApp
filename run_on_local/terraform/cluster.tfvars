# Variables to change for setting up the initial gateway VM

# The name of the cloud as given in the clouds.yml file
cloud_name = "openstack"

# Names for OpenStack items
network_name = "gateway-network"
router_name = "gateway-router"
keypair_name = "keypair"

# Path for the public key for the gateway VM
public_key_path = "/path/to/public/key"

# Settings for the Gateway VM
#   Image needs to be a recent Ubuntu version, tested with ubuntu-18.04
#   Flavor recommended large, e.g. 4 vCPUs and 16 GB RAM
gateway_name = "gateway"
gateway_image = "Ubuntu 18.04" 
gateway_flavor_id = "" 

# External network ID
external_network_id = ""
