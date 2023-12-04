from fastapi import FastAPI, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from pydantic import BaseModel

# Support get_todo_by_query_parameters function to return more than 1 todos as JSON
from typing import List, Optional

import mysql.connector
import socket

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str or None = None

class User(BaseModel):
    username: str
    email: str or None = None
    full_name: str or None = None
    disabled: bool or None = None

class UserInDB(User):
    hashed_password: str

# Database configuration
db_config = {
    "host": "mysql-svc",
    "user": "todo-app",
    "password": "fea8bbcf9c185f838a46ecb794e05efa60f35f22ed945875aa1d2160d7d618da",
    "database": "MySQLDB",
}

# Connect to the database
try:
    connection = mysql.connector.connect(**db_config)
    if connection.is_connected():
        print("Connected to the MySQL database")

except mysql.connector.Error as e:
    print("Error:", e)
    exit(1)

app = FastAPI()

class TodoCreate(BaseModel):
    title: str
    complete: bool = False

class TodoUpdate(BaseModel):
    id: int
    # Default values set to None so that if client doesn't provide these fields, API won't reject their requests
    title: Optional[str] = None
    complete: Optional[bool] = None

class Todo(BaseModel):

    id: int
    title: str
    complete: bool = False

    @staticmethod
    def get_todo_by_id(todo_id):
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cur:
                cur.execute("SELECT * FROM todo WHERE id = %s", (todo_id,))
                result = cur.fetchone()
                if result:
                    id, title, complete = result
                    return Todo(id=id, title=title, complete=complete)  # Using kwargs
                else:
                    raise HTTPException(status_code=404, detail=f"Todo ID:{todo_id} does not exist.")
    
    @staticmethod
    def get_todo_by_parameters( title, complete ):
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cur:
                criteria = ""
                if title is not None:
                    criteria = f" title = '{title}'"
                if complete is not None:
                    if criteria: 
                        criteria += f" AND complete = {complete}"
                    else:
                        criteria = f" complete = {complete}"
                cur.execute(f"SELECT * FROM todo WHERE {criteria}")
                # return a list of Todo's 
                # use list comprehension to build a list of Todo's from database fetch results
                return [Todo(id=id, title=title, complete=complete) for id, title, complete in cur.fetchall()]
    
    # get_todo_by_query_parameters -> Todo indicates this function will return class Todo objects, which means Todo.get_all should return class Todo instead of a list of dictionaries
    @staticmethod
    def get_all():
        cur = connection.cursor()
        cur.execute("SELECT * FROM todo")
        results = cur.fetchall()
        todos = []
        for result in results:
            id, title, complete = result
            todo = Todo(id=id, title=title, complete=complete)  
            todos.append(todo)
        cur.close()
        return todos
                
    @staticmethod
    def add(title, complete=False):
        cur = connection.cursor()
        cur.execute("INSERT INTO todo (title, complete) VALUES (%s, %s)", (title, complete))
        connection.commit()
        # Get the last inserted ID
        last_inserted_id = cur.lastrowid
        cur.close()
        return last_inserted_id

    @staticmethod
    def update(todo: "TodoUpdate"):        
        fields=[]
        values=[]
        for field, value in vars(todo).items():            
            # Do not add the following into "fields" variable
            # - key field, ie "id" 
            # - fields that are not included in the PUT request 
            if field == "id" or value == None:
                continue
            # Add single quotes around string values for UPDATE SQL statement
            if isinstance(value, str):
                fields.append(f"{field}=%s")                
                values.append(f"'{value}'")
            else:
                fields.append(f"{field}=%s")
                values.append(value)

        values.append(todo.id)  # Add the ID for the WHERE clause
        update_clause = f"UPDATE todo SET {', '.join(fields)} WHERE id=%s"
        full_query = update_clause % tuple(values)

        # If there are fields to update
        if fields:
            cur = connection.cursor()
            cur.execute(full_query)
            connection.commit()
            cur.close()
        else:
            raise HTTPException(status_code=204, detail="No fields provided for update")

    @staticmethod
    def delete(id):
        cur = connection.cursor()
        cur.execute("DELETE FROM todo WHERE id=%s", (id,))
        connection.commit()
        cur.close()

@app.get("/todos")
def get_todo_by_query_parameters(
    complete: bool | None = None ,
    title: str | None = None) -> List[Todo]:
    try:
        if title is None and complete is None:
            todos = Todo.get_all()
        else:
            todos = Todo.get_todo_by_parameters( title, complete )
        return todos
        
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {e}" )

@app.get("/todos/{todo_id}")
def get_todo_by_id(todo_id: int) -> Todo:
    try:
        todo = Todo.get_todo_by_id(todo_id)
        if todo:
            return todo
        else:
            raise HTTPException(status_code=404, detail="Todo not found")
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail="Database Error")

@app.post("/todos")
def add_todo(todo: TodoCreate):
    try:
        newID = Todo.add(todo.title, todo.complete)
        return Todo.get_todo_by_id(newID)
        
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail="Database Error")
    
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoUpdate):
    try:
        if Todo.get_todo_by_id(todo_id) is None:
            raise HTTPException(status_code=404, detail=f"Todo with ID:{todo_id} does not exist")
        else:
            Todo.update(todo)
            return Todo.get_todo_by_id(todo_id)
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database Error {e}")

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    try:
        if Todo.get_todo_by_id(todo_id) is None:
            raise HTTPException(status_code=404, detail=f"Todo with ID:{todo_id} does not exist")
        else:
            Todo.delete(todo_id)
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail="Database Error")
