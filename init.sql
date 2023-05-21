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