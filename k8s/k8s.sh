#!/bin/bash
# Create ConfigMap to run init.sql to create database / user / grant permission
kubectl apply -f mysql-init-configmap.yaml

# Create PersistentVolume and PersistentVolumeClaim    
    # Note - after making changes to PV, you must delete old one and apply again as PV is immutable
    # k delete pvc mysql-pv-claim
    # k delete pv mysql-pv-volume
        # If the above cmd was stuck / not returning, can try this one
        # k delete pv mysql-pv-volume --grace-period=0 --force

# Not needed after using StatefulSet and no pv is defined    
# k apply -f mysql-pv.yaml

# Create Deployment
kubectl apply -f mysql.yaml
kubectl rollout status statefulset mysql