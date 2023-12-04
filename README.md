# Project overview

The objective of this project is to learn/practice various aspects of DevOps through building and deploying a basic web app.

The app is packaged as a docker container and deployed on a kubernetes cluster.

This project is developed on my Windows PC with multiple ubuntu VMs on Virtualbox.  My project files are stored on Windows which can also be accessed on all VMs in /vagrant directory

If you have any suggestions or comments, please reach out at dleung331d@gmail.com

---
## VMs

| VM name      | Purpose                          |
|--------------|----------------------------------|
| k8s-main     | K8s control plane node           |
| k8s-worker-1 | K8s worker node                  |
| k8s-worker-2 | K8s worker node                  |
| k8s-control  | (optional) my dedicated dev environment |

Why I use control VM 
- dedicated dev env on Linux with the tools required for this project
- can be recreated with ease.  
- can manage k8s cluster without having to login the actual k8s nodes

You can also use your local machine (windows or mac or linux).  
Just install the tools that are needed for this project like docker, vagrant, ansible etc

---
## Directory structure and files

### root directory

- Vagrantfile         : spins up 1 VM as K8s control plane node and 2 VMs as worker nodes
                    : (optional) spins up 1 VM as dedicated dev environment (k8s-control VM)

- VM-IP-list.txt      : stores k8s VM IPs to be added in control VM's /etc/hosts file when vagrant up / vagrant provision is run

- app.py              : web app

- requirements.txt    : Python dependencies of web app

- docker-compose.yml  : run all components of the app (web and DB)

- Dockerfile          : builds the web app as Docker image

- init-MySQL.sql      : initialize MySQL DB (create user, table, insert some initial rows)

---
### ansible directory

- hosts               : groups VMs into control-plane and workers

- create_user.yaml    : creates user to install k8s as

- install_k8s.yaml    : installs k8s binaries

- cluster_init.yaml   : initializes k8s cluster 

- worker.yaml         : tells worker to join cluster

---
### k8s directory

- label-mysql-node.sh             : labels k8s-worker-1 as mysql node so that mysql pods only run on that node and creates a directory for storing MySQL data

- metallb_IP_pool.yaml            : defines a range of external IPs that can be assigned to LoadBalancer services

- metallb_L2_advertisement.yaml   : refers to the IP pool 

- mysql-init-configmap.yaml       : initialize MySQL DB (create user, table, insert some initial rows)

- mysql-pv.yaml                   : create persistent volume for MySQL

- mysql.yaml                      : define MySQL StatefulSet 

- storageClass.yaml               : create a local storage class that is used by MySQL to store data on local disk

- webpage_deployment.yaml         : define web app deployment

- webpage_lb_service.yaml         : sample LoadBalancer service for illustration purpose

---
#### ingress subdirectory

- ingress.yaml        : Create Ingress for routing external traffic to appropriate service based on URL

---
#### ssl-cert subdirectory

- cluster-issuer.yaml             : create Cluster Issuer 

- ingress-controller-cert.yaml    : control how often to renew the certificate

- ca-secret.yaml                  : store our dummy Certificate Authority's private key and certificate

---
## Completed tasks
- deployed the app on several VMs running as 1 kubernetes (k8s) control plane node and 2 worker nodes
- added API layer (basic)

---
## Feature wishlist
- CI/CD 
    - auto build/deploy different test envs
    - Automate testing
    - GitHub Actions
    - linting
    - ArgoCD
    - Sonarqube
- Deploy on AWS
    - Terraform
- API authentication 
- minimize manual installation steps

---
## Additional notes

### Aliases

I personally map "k" to kubectl command.

    alias k='kubectl'

usually the "cd" commands are relative to the project root directory

---
### Timeouts
If you aren't getting any output from kubectl command or timeouts, it may be because the VMs are maxing out CPU.  Just check your CPU usage and try again when the usage isn't as high

Example

vagrant@k8s-control:/vagrant/k8s$ k get pods

    Unable to connect to the server: net/http: TLS handshake timeout

vagrant@k8s-control:/vagrant/k8s$ k get pods

    NAME                                             READY   STATUS              RESTARTS   AGE
    my-webpage-adminer-deployment-66cf7465d4-xp4jr   1/1     Running             0          78s
    my-webpage-deployment-5b6fd7455c-gfqr9           0/1     ContainerCreating   0          78s
    mysql-0                                          2/2     Running             0          5m29s

---

# 2. Credits

I would like to thank the following content creators for their tutorials which this project is based on.

- Patrick Loeber - "Python Flask Beginner Tutorial - Todo App - Crash Course"
    - https://www.youtube.com/watch?v=yKHJsLUENl0&t=1952s

- DevOps Journey - "DevOps Lab Project - Learn to be a DevOps Engineer through this Practical Lab Project"
    - https://www.youtube.com/watch?v=YuZ002YrvUA&t=1619s

- Geeks Linux Video Tutorials - "Install Kubernetes Cluster With Ansible ▶ Install Kubernetes Cluster On Ubuntu in 5 minutes"
    - https://www.youtube.com/watch?v=B9_lUtCueKU&t=10s
    - https://www.linuxsysadmins.com/install-kubernetes-cluster-with-ansible/

- Engineering with Morris - MetalLB and NGINX Ingress // Setup External Access for Kubernetes Applications
    - https://www.youtube.com/watch?v=k8bxtsWe9qw&t=233s

- Christian Lempa - Free SSL Certs in Kubernetes! Cert Manager Tutorial
    - https://www.youtube.com/watch?v=DvXkD0f-lhY

- pixegami - PyTest • REST API Integration Testing with Python 
    - https://www.youtube.com/watch?v=7dgQRVqF1N0
    
# 
I am sure I missed some tutorials here and there.  Will try to add them back as soon as I remember which ones I missed.  

---

# 3. Setup (VMs and kubernetes)
Let's spin up the VMs and install kubernetes

###############################################<br>
###On Windows<br>
###############################################<br>
- Enable virtualization on Windows 
- Install vagrant, virtualbox
- Clone this repo 
    - (not tested) or copy this file (Vagrant/control/Vagrantfile) from this github repo to a brand new folder on Windows
- Open powershell, change directory to project root directory
- % vagrant up
- % vagrant ssh k8s-control

###############################################<br>
###On k8s-control VM as vagrant user:<br>
###############################################<br>

---
Check k8s VM IPs have been added in /etc/hosts by vagrant 

% cat /etc/hosts

---
Check ssh public and private keys are generated by vagrant successfully

% ls -la ~/.ssh/

---
### Copy ssh key to k8s VMs (default vagrant password is vagrant)

% ssh-copy-id -o StrictHostKeyChecking=no -i /home/vagrant/.ssh/id_ed25519.pub vagrant@k8s-main

% ssh-copy-id -o StrictHostKeyChecking=no -i /home/vagrant/.ssh/id_ed25519.pub vagrant@k8s-worker-1

% ssh-copy-id -o StrictHostKeyChecking=no -i /home/vagrant/.ssh/id_ed25519.pub vagrant@k8s-worker-2

---
Verify connectivity to k8s VMs

% ssh k8s-main

% ssh k8s-worker-1

% ssh k8s-worker-2

---
Change to project root directory

% cd /vagrant

---
### Run ansible playbooks to configure k8s on k8s VMs

% cd /vagrant/ansible

% ansible-playbook create_user.yaml -i hosts -k -K
    
    SSH password:vagrant
    
    SUDO password:vagrant
    
    Account need to be create in remote server:ansible
    
        Yes, probably can use a better name as this user will be used to install k8s.  Feel free to change it and in subsequent yaml files

% ansible-playbook install_k8s.yaml -i hosts 

% vi cluster_init.yaml
    replace the IPs in "Initializing Kubernetes Cluster" step  with your k8s-main VM's subnet mask and IP 

% ansible-playbook cluster_init.yaml -i hosts -K

% ansible-playbook worker.yaml -i hosts -K

---
### Add cluster info from k8s-main VM in control VM so that we can use kubectl to access this cluster from control VM

% mkdir ~/.kube

% vi ~/.kube/config

    paste the contents from k8s-main VM's ~ansible/.kube/config file
Save and exit vi

---
Verify all nodes are on the cluster

% k get nodes

    NAME         STATUS   ROLES           AGE   VERSION
    k8s-main   Ready    control-plane   64m   v1.25.0
    k8s-worker-1   Ready    <none>          55m   v1.25.0
    k8s-worker-2   Ready    <none>          55m   v1.25.0

If k get nodes seems unresponsive, it may be because k8s control plane isn't ready yet.  You can check its status on k8s-main node

% ssh k8s-main

###############################################<br>
###On k8s-main VM as vagrant user:<br>
###############################################<br>

% sudo su - ansible

% kubectl get nodes

% kubectl describe node k8s-main

    ...
    Events:
    Type     Reason                   Age                From             Message
    ----     ------                   ----               ----             -------
    Normal   Starting                 9m55s              kube-proxy
    Normal   Starting                 10m                kubelet          Starting kubelet.
    Warning  InvalidDiskCapacity      10m                kubelet          invalid capacity 0 on image filesystem
    Normal   NodeAllocatableEnforced  10m                kubelet          Updated Node Allocatable limit across pods
    Normal   RegisteredNode           9m56s              node-controller  Node k8s-main event: Registered Node k8s-main in Controller
    Normal   NodeNotReady             14s (x3 over 7m)   node-controller  Node k8s-main status is now: NodeNotReady
    Normal   NodeHasSufficientMemory  4s (x4 over 10m)   kubelet          Node k8s-main status is now: NodeHasSufficientMemory
    Normal   NodeHasNoDiskPressure    4s (x4 over 10m)   kubelet          Node k8s-main status is now: NodeHasNoDiskPressure
    Normal   NodeHasSufficientPID     4s (x4 over 10m)   kubelet          Node k8s-main status is now: NodeHasSufficientPID
    Normal   NodeReady                4s (x4 over 9m7s)  kubelet          Node k8s-main status is now: NodeReady

Just give it some time for it to come online

---
### Verify pods (only system pods are running at the moment)
###############################################<br>
###On k8s-control VM as vagrant user:<br>
###############################################<br>
% k get pods -A

    NAMESPACE     NAME                                       READY   STATUS    RESTARTS   AGE
    kube-system   calico-kube-controllers-5f85948b55-jzrn4   1/1     Running   0          64m
    kube-system   calico-node-gwhzn                          1/1     Running   0          64m
    kube-system   calico-node-k887z                          1/1     Running   0          55m
    ...

---
### Verify all nodes are on the cluster

% k get nodes

    NAME         STATUS   ROLES           AGE   VERSION
    k8s-main   Ready    control-plane   64m   v1.25.0
    k8s-worker-1   Ready    <none>          55m   v1.25.0
    k8s-worker-2   Ready    <none>          55m   v1.25.0

There is a known issue where k8s uses IP from VM's eth0 interface instead of eth1.  As a result, when you run kubectl logs <pod>, it cannot reach the node using the correct IP (eth1)

See https://github.com/halfcrazy/website/commit/a64edb86b5e753215529fdb73b1c58796559faee

To fix this, set eth1 IP in KUBELET_EXTRA_ARGS variable

###############################################<br>
###On all k8s VMs as vagrant user:<br>
###############################################<br>

% sudo su

% cp /etc/systemd/system/kubelet.service.d/10-kubeadm.conf /etc/systemd/system/kubelet.service.d/10-kubeadm.conf.orig

% vi /etc/systemd/system/kubelet.service.d/10-kubeadm.conf

    Set KUBELET_EXTRA_ARGS to VM IP 
    For example, my k8s-main VM is 192.168.150.10
        Environment="KUBELET_EXTRA_ARGS=--node-ip=192.168.150.10"
    k8s-worker-1
        Environment="KUBELET_EXTRA_ARGS=--node-ip=192.168.150.11"
    k8s-worker-2
        Environment="KUBELET_EXTRA_ARGS=--node-ip=192.168.150.12"

Save and exit vi

---
# 4. Setup (Build app)

###############################################<br>
###On k8s-control VM as vagrant user:<br>
###############################################<br>

% cd /vagrant

Build docker image and push to DockerHub

% docker build -t \<user\>/my-webpage .
    
    For example, docker build -t dleung331d/my-webpage .

% docker login

% docker push \<user\>/my-webpage

---
## Configure k8s

% cd /vagrant/k8s

Create local storage class

% k apply -f storageClass.yaml

---
## Deploy mysql
% cd /vagrant/k8s

% k apply -f mysql-init-configmap.yaml

% k apply -f mysql-pv.yaml

% k apply -f mysql.yaml

Label k8s-worker-1 as mysql node and create persistent volume 

% ./label-mysql-node.sh

It will take some time for mysql to come up.  You can monitor its status while proceeding to deploy webpage

% k get pods --watch

---
## Deploy webpage
% k apply -f webpage_deployment.yaml

% k get pods

    NAME                                             READY   STATUS    RESTARTS      AGE
    my-webpage-adminer-deployment-66cf7465d4-lph7d   1/1     Running   0             5m42s
    my-webpage-deployment-5b6fd7455c-mhvkd           1/1     Running   0             5m42s
    mysql-0                                          2/2     Running   2 (21m ago)   20h

Once the pods are up and running, run a curl command to verify the app is working

% k get svc

    NAME                     TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
    kubernetes               ClusterIP   10.96.0.1        <none>        443/TCP    2d22h
    my-webpage-adminer-svc   ClusterIP   None             <none>        8080/TCP   3m18s
    my-webpage-svc           ClusterIP   10.104.114.254   <none>        80/TCP     3m18s
    mysql-read               ClusterIP   10.96.54.206     <none>        3306/TCP   2d2h
    mysql-svc                ClusterIP   None             <none>        3306/TCP   2d2h

Note you need to run the curl command on k8s-main VM for now because k8s-control is outside the cluster.  My-webpage-svc is a clusterIP which is only accessible within the cluster

###############################################<br>
###On k8s-main VM as vagrant user:<br>
###############################################<br>
Curl my-webpage-svc's IP at port 80.  You should get html tags

% curl 10.104.114.254

    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    ...

---
## Deploy load balancer 

Let's now set up a load balancer so we can connect to the app from outside the cluster (for ex. local machine)

Please refer to this great tutorial for details
- Engineering with Morris - MetalLB and NGINX Ingress // Setup External Access for Kubernetes Applications
    - https://www.youtube.com/watch?v=k8bxtsWe9qw&t=233s

---
###############################################<br>
###On k8s-control VM as vagrant user:<br>
###############################################<br>

Install metallb load balancer by following the below steps.  For reference, you can also check https://metallb.universe.tf/installation/

---
Dry-run to set strictARP to true 

% k get configmap kube-proxy -n kube-system -o yaml | sed -e "s/strictARP: false/strictARP: true/" | kubectl diff -f - -n kube-system

    @@ -33,7 +33,7 @@
        excludeCIDRs: null
        minSyncPeriod: 0s
        scheduler: ""
    -      strictARP: false
    +      strictARP: true
        syncPeriod: 0s
        tcpFinTimeout: 0s
        tcpTimeout: 0s

Apply the changes (returns nonzero returncode on errors only)

% k get configmap kube-proxy -n kube-system -o yaml | sed -e "s/strictARP: false/strictARP: true/" | kubectl apply -f - -n kube-system

    Warning: resource configmaps/kube-proxy is missing the kubectl.kubernetes.io/last-applied-configuration annotation which is required by kubectl apply. kubectl apply should only be used on resources created declaratively by either kubectl create --save-config or kubectl apply. The missing annotation will be patched automatically.
    configmap/kube-proxy configured

---
Install metallb

% k apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.10/config/manifests/metallb-native.yaml


Verify there are 1 metallb controller and 3 speaker pods (1 for each node)

% k get pods -n metallb-system -o wide

    NAME                          READY   STATUS    RESTARTS   AGE   IP                NODE         NOMINATED NODE   READINESS GATES
    controller-66d6955457-zk59s   1/1     Running   0          75s   192.168.100.198   k8s-worker-2   <none>           <none>
    speaker-qk727                 1/1     Running   0          75s   192.168.150.11    k8s-worker-1   <none>           <none>
    speaker-rmjm8                 1/1     Running   0          75s   192.168.150.12    k8s-worker-2   <none>           <none>
    speaker-tt62x                 1/1     Running   0          75s   192.168.150.10    k8s-main   <none>           <none>

Verify there are 7 resources installed

% k api-resources | grep metal

---
Create IP pool 

I picked a IP range in the same subnet as my VMs.  Ex. my VMs are on 192.168.150.10-12.  I assigned ext IP range btwn 192.168.150.200-250 in metallb_IP_pool.yaml)

% cd /vagrant/k8s

% k apply -n metallb-system -f metallb_IP_pool.yaml

% k -n metallb-system get IPAddressPool

---
Create L2 advertisement

% k apply -f metallb_L2_advertisement.yaml

% k get l2advertisement -n metallb-system


---
Create load balancer service to connect to pods running our app (app: my-webpage)

% k apply -f webpage_lb_service.yaml

% k get svc

    NAME                     TYPE           CLUSTER-IP       EXTERNAL-IP       PORT(S)        AGE
    kubernetes               ClusterIP      10.96.0.1        <none>            443/TCP        2d23h
    my-webpage-adminer-svc   ClusterIP      None             <none>            8080/TCP       35m
    my-webpage-lb-svc        LoadBalancer   10.103.19.54     192.168.150.200   80:32185/TCP   5s        
    my-webpage-svc           ClusterIP      10.104.114.254   <none>            80/TCP         35m
    mysql-read               ClusterIP      10.96.54.206     <none>            3306/TCP       2d3h
    mysql-svc                ClusterIP      None             <none>            3306/TCP       2d3h

Note - external client can connect via LoadBalancer service (ext IP:192.168.150.200) or aliases that are mapped to this IP

If I want to access this using URL on my Windows, I can add this entry in C:\Windows\System32\drivers\etc\hosts file

    192.168.150.200 mywebpage-no-ingress.com

Open browser and enter http://mywebpage-no-ingress.com.  You should be able to view the webpage.


LoadBalancer Service my-webpage-lb-svc is just for illustration purpose.  A better way to allow external traffic to be routed to our app is by using Ingress (see next section).  

Ingress is better than the example above because you just need 1 ext IP for it.  It can help to route different URLs to whichever clusterIP service that you want.  So you don't need to define a LoadBalancer Service for each component of your app that accepts outside traffic

---
## Deploy Ingress Controller 

Please refer to this great tutorial for details
- Engineering with Morris - MetalLB and NGINX Ingress // Setup External Access for Kubernetes Applications
    - https://www.youtube.com/watch?v=k8bxtsWe9qw&t=233s


Ingress Controller routes requests from outside k8s cluster to the desired services/pods (based on URL)

% cd /vagrant/k8s/ingress

---
Install helm

% curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3

% chmod 700 get_helm.sh

% ./get_helm.sh

---
Download cfg files

% helm pull oci://ghcr.io/nginxinc/charts/nginx-ingress --untar --version 0.17.1

% cd /vagrant/k8s/ingress/nginx-ingress

% k create ns nginx-ingress

Switch to nginx-ingress namespace.  If kubens isn't installed, use kubectl config set-context

% k config set-context --current --namespace=nginx-ingress

or

% kubens nginx-ingress

% k apply -f crds

% helm install nginx-ingress oci://ghcr.io/nginxinc/charts/nginx-ingress --version 0.17.1

External IP is assigned to controller 

% k get svc
    NAME                       TYPE           CLUSTER-IP      EXTERNAL-IP       PORT(S)                      AGE
    nginx-ingress-controller   LoadBalancer   10.97.219.218   192.168.150.201   80:31745/TCP,443:30028/TCP   67s


% cd /vagrant/k8s

---
Change default namespace back to default

% k config set-context --current --namespace=default

Verify we are in default namespace

% k get svc

    NAME                     TYPE           CLUSTER-IP       EXTERNAL-IP       PORT(S)        AGE
    kubernetes               ClusterIP      10.96.0.1        <none>            443/TCP        51m
    my-webpage-adminer-svc   ClusterIP      None             <none>            8080/TCP       23m
    my-webpage-lb-svc        LoadBalancer   10.96.112.31     192.168.150.200   80:30364/TCP   12m
    my-webpage-svc           ClusterIP      10.98.111.97     <none>            80/TCP         23m
    mysql-read               ClusterIP      10.106.242.242   <none>            3306/TCP       28m
    mysql-svc                ClusterIP      None             <none>            3306/TCP       28m


---
### SSL certificate (self signed)

To test the app through https://mywebpage.com, let's create a self signed certificate.

Please refer to this great tutorial for details
Christian Lempa - Free SSL Certs in Kubernetes! Cert Manager Tutorial
    - https://www.youtube.com/watch?v=DvXkD0f-lhY

---
Install cert-manager 

% k apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml

---
Create a Certificate Authority a. Create a CA private key

% cd /vagrant/k8s/ssl-cert

% openssl genrsa -out ca.key 4096

---
Create a CA certificate

% openssl req -new -x509 -sha256 -days 365 -key ca.key -out ca.crt

---
Convert the content of the key and crt to base64 oneline

% cat ca.crt | base64 -w 0

% cat ca.key | base64 -w 0

Put the above command outputs in ca-secret.yaml 

    data:
    tls.crt:  <cat ca.crt | base64 -w 0>
    tls.key:  <cat ca.key | base64 -w 0>

---
Create secret 

% k apply -f ca-secret.yaml

---
Create a cluster issuer object

% k apply -f cluster-issuer.yaml

---
Create a new certificate 

% k apply -f ingress-controller-cert.yaml

---
Create Ingress

% cd /vagrant/k8s/ingress

% k apply -f ingress.yaml

If I want to access this using URL on my Windows, I can add this entry in C:\Windows\System32\drivers\etc\hosts file

    192.168.150.201 mywebpage.com

Open https://mywebpage.com.  The browser should show "Your connection is not private..."

To resolve this warning, import the CA certificate in the trusted Root Ca store of your clients

On Windows
- Double click on ca.crt
- Click Install Certificate
- Select Local Machine
- Place all certificates in the following store > Browse > Trusted Root Cert. Authorities


To change how long the certificate is valid for / change certificate validty / change certificate time
- add "duration" in yaml

        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
        name: ingress-controller-cert
        spec:
        secretName: tls-secret
        issuerRef:
            name: myclusterissuer
            kind: ClusterIssuer
        duration: 24h
        dnsNames:
            - mywebpage.com

- % k delete tls-secret

- % k apply -f ingress-controller-cert.yaml

- Clear browser cache / restart browser if needed

---


# 5. Alternate Setup (Run on Docker)

###############################################<br>
###On k8s-control VM as vagrant user:<br>
###############################################<br>

% cd /vagrant

% docker-compose up -d


###############################################<br>
###On Windows<br>
###############################################<br>

    Open browser and go to http://<k8s-control IP address>:5000



# 6. API 

API component is being developed at the moment.  For simplicity, it is being tested by running the app on docker instead of k8s.

## Setup

###############################################<br>
###On Windows<br>
###############################################<br>

% vagrant up k8s-control

% vagrant ssh k8s-control

###############################################<br>
###On k8s-control VM as vagrant user:<br>
###############################################<br>

% cd /vagrant

% docker-compose up -d --build

All 4 components should be running (api, my-webpage, MySQL-svc, adminer)

% docker ps 
```bash
vagrant@k8s-control:/vagrant$ docker ps
CONTAINER ID   IMAGE                COMMAND                  CREATED
STATUS          PORTS                                       NAMES
086b4eaee0c4   vagrant_api          "uvicorn fastapi-mai…"   13 minutes ago   
Up 13 minutes   0.0.0.0:80->80/tcp, :::80->80/tcp           api
f66d86694844   vagrant_my-webpage   "flask run"              21 minutes ago   
Up 21 minutes   0.0.0.0:5000->5000/tcp, :::5000->5000/tcp   my-webpage        
c72837a1e011   adminer              "entrypoint.sh php -…"   3 weeks ago      
Up 23 minutes   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   adminer
1f50d5fb49f7   mysql                "docker-entrypoint.s…"   3 weeks ago      
Up 23 minutes   3306/tcp, 33060/tcp                         mysql
```

###############################################<br>
###On Windows<br>
###############################################<br>

To test FastAPI via browser, open 
    
    http://<k8s-control IP address>/docs

To test FastAPI via pytest, run tests/test_api.py on k8s-control VM

    cd /vagrant
    pytest tests/test_api.py

To access Todo webapp, open browser
    
    http://<k8s-control IP address>:5000

# End
