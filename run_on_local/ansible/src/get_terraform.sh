mkdir terraform-"$1"
cd terraform-"$1"
wget https://releases.hashicorp.com/terraform/"$1"/terraform_"$1"_linux_amd64.zip
sudo apt install unzip
unzip terraform_"$1"_linux_amd64.zip 
sudo mv terraform /usr/local/bin