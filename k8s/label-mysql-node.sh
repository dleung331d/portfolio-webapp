#!/bin/bash
# Run this script on control node to label mysql node and create mysql-data directory on remote host to persist mysql pod's data
# 

# Set the node name that you want MySQL to run on 
NODE_NAME="k8s-worker-1"

# Label the node
echo "Labelling $NODE_NAME with app=mysql"
# If node is already labelled and this command is executed, output will show "node/<node> not labelled".  
# Avoid confusion by not displaying output at all
kubectl label nodes $NODE_NAME app=mysql > /dev/null
echo "Done"
echo 

echo "Checking label on $NODE_NAME"
kubectl get node $NODE_NAME --show-labels
echo 

echo "Creating /mnt/mysql-data on $NODE_NAME"
ssh vagrant@$NODE_NAME "sudo mkdir -p /mnt/mysql-data"
echo "Done"
echo 

echo "Verifying /mnt/mysql-data on $NODE_NAME"
ssh vagrant@$NODE_NAME "sudo ls -ld /mnt/mysql-data"
echo

echo "End of script"