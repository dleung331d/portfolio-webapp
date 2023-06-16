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
https://kubernetes.io/docs/tasks/run-application/run-replicated-stateful-application/
Assuming you are starting this StatefulSet for the first time
MySQL will run init.sql to create DB, user and table

% cd /home/dleung331d/webpage/k8s
% ./k8s.sh

Terminal A
% k get pods --watch

Terminal B
% k logs mysql-0 -f

Connect to MySQL client
% kubectl exec -it mysql-0 -- bash -c "mysql -u root -h localhost"
    or 
    % kubectl exec -it mysql-0 bash
    % mysql -u root -h localhost

    or
    Start a new pod to run mysql client
    % kubectl run -it --rm --image=mysql --restart=Never mysql-client -- mysql -h mysql -ppassword

In MySQL, check changes in init.sql are applied

For example
mysql> use MySQLDB; select * from todo;
+----+------------------------------------+----------+
| id | title                              | complete |
+----+------------------------------------+----------+
|  1 | A                                  |        0 |
|  2 | Init.sql ran - 2023-06-09 00:52:33 |        0 |
+----+------------------------------------+----------+

Delete pod to check data persistency
% k delete pod mysql-0; k get pods --watch

After MySQL pod is restarted, check logs when DB is up 
% k logs mysql-0 -f

Verify that init.sql is not executed again.  MySQLDB.todo table should have same entries as init.sql
% kubectl exec -it mysql-0 -- bash -c "mysql -u root -h localhost"
mysql> use MySQLDB; select * from todo;
+----+------------------------------------+----------+
| id | title                              | complete |
+----+------------------------------------+----------+
|  1 | A                                  |        0 |
|  2 | Init.sql ran - 2023-06-09 00:52:33 |        0 |
+----+------------------------------------+----------+

Insert a row in todo table.  Restart pod.  Check if data is persisted.

