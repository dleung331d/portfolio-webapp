-- This file was only used during initial stages of dev before running the app on k8s.
-- After the app has migrated to k8s, these initial sql steps have been configured as k8s configmap (see mysql-init-configmap.yaml)
CREATE DATABASE IF NOT EXISTS MySQLDB;
USE MySQLDB;

-- CREATE USER username@host (% means user can connect from any host)
-- try setting host as "myflaskwebservice" ??
CREATE USER IF NOT EXISTS 'todo-app'@'%' IDENTIFIED WITH mysql_native_password BY 'fea8bbcf9c185f838a46ecb794e05efa60f35f22ed945875aa1d2160d7d618da' ;

CREATE TABLE IF NOT EXISTS todo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    complete boolean
);

GRANT ALL PRIVILEGES ON MySQLDB.* TO 'todo-app'@'%';

-- Check if the todo table is empty before inserting some sample data rows
DROP PROCEDURE IF EXISTS PopulateTodo;
DELIMITER //
CREATE PROCEDURE PopulateTodo()
BEGIN
    SELECT COUNT(*) AS count FROM todo INTO @rowCount;
    IF @rowCount = 0 THEN
        select "Table is empty";
        INSERT INTO todo ( title, complete) values ( CONCAT( 'init-MySQL.sql ran - ', DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s') ), FALSE);
        INSERT INTO todo ( title, complete) values ( 'Todo item 1 inserted by init-MySQL.sql', FALSE);
        INSERT INTO todo ( title, complete) values ( 'Todo item 2 inserted by init-MySQL.sql', FALSE);
    END IF;
END //
DELIMITER ;

CALL PopulateTodo();

