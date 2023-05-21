#   render_template - return html template 
#   request         - get input from user when they click button
#   redirect        - refresh HTML page after user adds new todo
#   url_for         - class for building URL?
from flask import Flask, request, render_template, redirect, url_for
from flask_mysqldb import MySQL

# to get vm hostname
import socket

# Tried adding timezone to log entries but doesn't work.  Can see timestamp only for now
import logging
import datetime

# Set up logging configuration
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s - %(message)s')
# Tried adding timezone to log entries but doesn't work.  Can see timestamp only for now
#logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %Z%z - %(levelname)s - %(message)s')

# Get the root logger
logger = logging.getLogger()

# Create a formatter with a custom date/time format
formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')

# Create a handler for logging to a file
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

logging.info('DLTEST Initializing Flask')
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'todo-app'
app.config['MYSQL_PASSWORD'] = 'fea8bbcf9c185f838a46ecb794e05efa60f35f22ed945875aa1d2160d7d618da'
app.config['MYSQL_DB'] = 'MySQLDB'

logging.info('DLTEST MySQL')
mysql = MySQL(app)


class Todo:
    def __init__(self, id, title, complete):
        self.id = id
        self.title = title
        self.complete = complete

    @staticmethod
    def get_all():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM todo")
        results = cur.fetchall()
        todos = []
        for result in results:
            id, title, complete = result
            todo = Todo(id, title, complete)
            todos.append(todo)
        cur.close()
        return todos

    @staticmethod
    def add(title):
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO todo (title, complete) VALUES (%s, %s)", (title, False))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def update(id, title, complete):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE todo SET title=%s, complete=%s WHERE id=%s", (title, complete, id))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def delete(id):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM todo WHERE id=%s", (id,))
        mysql.connection.commit()
        cur.close()


@app.route('/')
def index():
    logging.info('DLTEST route /')
    todos = Todo.get_all()
    hostname = socket.gethostname()
    ipaddr = socket.gethostbyname(hostname)
    return render_template('index.html', todo_list=todos, hostname=hostname, ipaddr=ipaddr)

# Use <form method="POST"> to submit request
@app.route('/add', methods=['POST'])
def add():
    logging.info('DLTEST route /add')
    title = request.form['title']
    Todo.add(title)
    return redirect(url_for('index'))

# Use <form method="POST"> to submit request
@app.route('/update/<int:id>', methods=['POST'])
def update(id):    
    logging.info('DLTEST route /update')
    # Fetch 
    cur = mysql.connection.cursor()
    cur.execute("SELECT title, complete FROM todo WHERE id=%s", (id,))
    result = cur.fetchone()
    
    title  = result[0]
    complete = result[1]
    cur.close()

    Todo.update(id, title, not complete)
    return redirect(url_for('index'))

# Use <form method="POST"> to submit request
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    logging.info('DLTEST route /delete')
    Todo.delete(id)
    return redirect(url_for('index'))


# DL: app.run will be executed by docker, so don't need this
# if __name__ == '__main__':
#     app.run(debug=True)
