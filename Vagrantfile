#########################################
# General 
#########################################
VM_PREFIX="k8s"
IMAGE_NAME = "bento/ubuntu-18.04"

#########################################
# Application VMs
#########################################

# Assumption
# K8s control plane node will be assigned IP as "PREFIX.SUFFIX"
# K8s worker nodes will be assigned IPs as PREFIX.SUFFIX + 1, 2, etc...
APP_VM_IP_PREFIX    = "192.168.150"
APP_VM_IP_SUFFIX    = 30
APP_VM_NET_MASK     = "255.255.255.0"

# K8s control plane node

# K8s worker nodes
# number of VMs as K8s worker nodes
N = 2


#########################################
# Control VM
#########################################
CONTROL_VM_ENABLE   = 1
CONTROL_VM_IP       = "192.168.150.4"
CONTROL_VM_NET_MASK = "255.255.255.0"

Vagrant.configure("2") do |config|
    config.ssh.insert_key = false

    config.vm.define "#{VM_PREFIX}-main" do |main|
        main.vm.box = IMAGE_NAME        
        
        main.vm.network "private_network", ip: "#{APP_VM_IP_PREFIX}.#{APP_VM_IP_SUFFIX}"
        main.vm.hostname = "#{VM_PREFIX}-main"
        main.vm.provider "virtualbox" do |vb|
            vb.name = "#{VM_PREFIX}-main"
            vb.customize ["modifyvm", :id, "--memory", 3072]
            # K8s control plane requires 2 CPU
            vb.customize ["modifyvm", :id, "--cpus", 2]
            # Disable nested paging to avoid constant high CPU usage by VM
            vb.customize ["modifyvm", :id, "--nestedpaging", "off"]
        end
        main.vm.provision "shell", inline: <<-SHELL
            echo "alias k='kubectl'" >> ~/.bashrc
            source ~/.bashrc
        SHELL
    end

    (1..N).each do |i|
        config.vm.define "#{VM_PREFIX}-worker-#{i}" do |node|
            node.vm.box = IMAGE_NAME
            node.vm.network "private_network", ip: "#{APP_VM_IP_PREFIX}.#{i + APP_VM_IP_SUFFIX}", netmask: APP_VM_NET_MASK
            node.vm.hostname = "#{VM_PREFIX}-worker-#{i}"
            node.vm.provider "virtualbox" do |vb|
                vb.name = "#{VM_PREFIX}-worker-#{i}"
                vb.customize ["modifyvm", :id, "--memory", 2048]
                vb.customize ["modifyvm", :id, "--cpus",  1]
                # Disable nested paging to avoid constant high CPU usage by VM
                vb.customize ["modifyvm", :id, "--nestedpaging", "off"]
            end
            node.vm.provision "shell", inline: <<-SHELL
                echo "alias k='kubectl'" >> ~/.bashrc
                source ~/.bashrc
            SHELL
        end
    end

    if CONTROL_VM_ENABLE == 1
        config.vm.define "#{VM_PREFIX}-control" do |control|
            control.vm.box = IMAGE_NAME
            control.vm.hostname = "#{VM_PREFIX}-control"
            # Force Virtualbox hostname to be vm1 instead of current directory
            control.vm.provider "virtualbox" do |vb|
              vb.name = "#{VM_PREFIX}-control"
              vb.customize ["modifyvm", :id, "--memory", 3072]
              vb.customize ["modifyvm", :id, "--cpus", 1]
              # Disable nested paging to avoid constant high CPU usage by VM
              vb.customize ["modifyvm", :id, "--nestedpaging", "off"]
            end
            # End force
        
            # Pick a IP from one of the subnets listed in your VirtualBox's Network Manager
            # VirtualBox > File > Tools > Network Manager
            control.vm.network "private_network", ip: CONTROL_VM_IP, netmask: CONTROL_VM_NET_MASK

            # Expose ports used by Docker containers for testing with Windows browser 
            control.vm.network "forwarded_port", guest: 5000, host: 5000
            control.vm.network "forwarded_port", guest: 8080, host: 8080

            config.vm.provision "shell", inline: <<-SHELL
        
                # Add aliases
                if ! grep -q "alias k='kubectl'" ~vagrant/.bashrc; then
                    echo "alias k='kubectl'" >> ~vagrant/.bashrc
                fi
            
                # Add k8s VM IPs in hosts file to /etc/hosts
                # Check if each line from /vagrant/hosts (our k8s VM IPs) is present in the VM's /etc/hosts file
                
                # Path to the hosts file inside the VM
                HOSTS_FILE="/etc/hosts"
            
                # Path to the hosts file on the host machine
                K8S_VM_IP_FILE="/vagrant/VM-IPs.txt"
                while IFS= read -r line; do
                    if ! grep -q "$line" "$HOSTS_FILE"; then
                    echo "Adding $line to $HOSTS_FILE"
                    echo "$line" >> $HOSTS_FILE 
                    fi
                done < "$K8S_VM_IP_FILE"
            
                # Check if SSH key already exists on k8s-master VM
                if ! [ -f /home/vagrant/.ssh/id_ed25519 ] ; then
                    # Generate SSH key if it doesn't exist
                    sudo -u vagrant ssh-keygen -t ed25519 -C "vagrant" -f /home/vagrant/.ssh/id_ed25519 -N ""
            
                    # Copy SSH key to k8s-master without prompting
                    # sudo -u vagrant ssh-copy-id -o StrictHostKeyChecking=no -i /home/vagrant/.ssh/id_ed25519.pub vagrant@k8s-main vagrant@k8s-worker-1 vagrant@k8s-worker-2
                    # config.vm.provision "file", source: "/home/vagrant/.ssh/id_ed25519.pub", destination: "~/.ssh/authorized_keys"
                fi
            
                # Before any installations
                sudo apt-get update

                # Install curl
                if ! command -v curl &> /dev/null; then
                    sudo apt-get install -y curl
                fi
                
                # Install git
                if ! command -v git &> /dev/null; then
                    sudo apt-get install -y git
                fi

                # Install dos2unix
                if ! command -v dos2unix &> /dev/null; then
                    sudo apt-get install -y dos2unix
                fi

                # Install Docker
                if ! command -v docker &> /dev/null; then
                    curl -fsSL https://get.docker.com -o get-docker.sh
                    sh get-docker.sh
                    rm get-docker.sh
                    sudo usermod -aG docker vagrant
                    sudo apt install -y docker-compose
                fi
            
                # Install Ansible
                if ! command -v ansible &> /dev/null; then
                    # Install latest ansible by adding ansible PPA to make use of reboot module (added in v2.7) but Ubuntu 18.04 has v2.5 only
                    sudo apt-add-repository --yes --update ppa:ansible/ansible
                    sudo apt-get install -y ansible
                    # sshpass is required for ansible to connect with password via ssh 
                    sudo apt-get install -y sshpass
                fi
            
                # Install kubectl
                if ! command -v kubectl &> /dev/null; then
                    # Install necessary packages for kubectl
                    sudo apt-get install -y apt-transport-https ca-certificates curl
                    
                    # Download and install kubectl (Match the k8s version you want to install on k8s VMs)
                    curl -LO "https://dl.k8s.io/release/v1.25.8/bin/linux/amd64/kubectl"
                
                    sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
                    
                    # Verify kubectl installation
                    kubectl version --client
                    
                    # Clean up downloaded files
                    rm kubectl
                fi
            SHELL
        end
    end
end
