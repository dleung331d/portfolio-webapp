My website with a To-do app

Todos
Start MySQL
how to encrypt mysql password in docker / k8s

Run steps
# Start webpage using docker 
% docker compose up -d
    old way - when Docker Desktop was installed
    Seems command name is different from installing docker directly in WSL Ubuntu 
     % docker-compose up -d --build
     
# Start MySQL with K8s
https://kubernetes.io/docs/tasks/run-application/run-single-instance-stateful-application/
% cd k8s
% k apply -f mysql.yaml

Terminal A
% k get pods --watch

Terminal B
% k logs mysql-6d5d8df769-hnh7g -f

Start a pod to connect to MySQL server
% kubectl run -it --rm --image=mysql --restart=Never mysql-client -- mysql -h mysql -ppassword

