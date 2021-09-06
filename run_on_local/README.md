## Setup the Gateway VM

In order to setup the Gateway VM from you local computer you will need the following

 * A login to your OpenStack cloud using for example the `~/.config/openstack/clouds.yml` file.
 * ansible (tested with 2.8.5)
 * terraform (tested with 0.15.1)

Instructions

* Generate a SSH keypair using e.g. `ssh-keygen`.

* Update the `terrafrom/cluster.tfvars` file to add the following

    * Path to the SSH key,
    * OpenStack external network ID,
    * Gateway VM image ID and flavor.
* Visit the `terraform/` folder and run

  ```
  terraform init
  terraform apply -var-file=cluster.tfvar
  ```

  Note the public IP generated.

* Add the Gateway VM key to your ssh agent

  ````bash
  eval $(ssh-agent -s)
  ssh-add /path/to/your/private/key
  ````

* Visit the `ansible/` folder and setup the Gateway VM by running the following two ansible scripts.

  ````
  ansible-playbook -i inventory/gateway copy_code.yml
  ansible-playbook -i inventory/gateway setup_gateway.yml
  ````


Now SSH into the Gateway VM with  `ssh ubuntu@GATEWAY-IP` and go to the `run_on_gateway/` folder for the next step in the setup. 

