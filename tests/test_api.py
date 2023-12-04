# For simplicity, I am using requests module for testing
# Perhaps requests module can be used as integration test
# ..and TestClient can be unit test
#
# Tutorials:
# - pixegami - PyTest • REST API Integration Testing with Python (https://www.youtube.com/watch?v=7dgQRVqF1N0)
# 
import requests
from pydantic import BaseModel
from typing import Optional 

ENDPOINT = "http://localhost"

class CreateTodo(BaseModel):
    title: str
    complete: Optional[bool] = False

class Todo(BaseModel):
    id: int
    title: str
    complete: bool

class UpdateTodo(BaseModel):
    id: int
    title: Optional[str] = None
    complete: Optional[bool] = None

def test_read_all_todo():
    response = requests.get(ENDPOINT + "/todos")
    assert response.status_code == 200
    data = response.json()

def test_create_todo():

    # response = requests.post(f"{ENDPOINT}/todos/", json=new_todo)
    new_todo = generate_todo()
    response = send_create_todo( new_todo )
    assert response.status_code == 200
    data = response.json()
    
    new_todo_id = data["id"]
    assert data["title"] == new_todo.title
    assert data["complete"] == False
    
    # Check the new todo item is created correctly on server side
    get_todo_response = send_get_todo(new_todo_id)
    assert get_todo_response.status_code == 200
    get_todo_data = get_todo_response.json()
    
    assert get_todo_data["title"] == new_todo.title
    assert get_todo_data["complete"] == False

    new_todo_object = Todo(**response.json())
    return new_todo_object

def test_update_todo_supply_all_fields():    
    todo_object = test_create_todo()
    todo_object.title = todo_object.title + " amended by test_update_todo_all_fields"
    update_todo_response = send_update_todo(todo_object)
    update_todo_response_data = update_todo_response.json()
    assert update_todo_response.status_code == 200
    assert update_todo_response_data["id"] == todo_object.id
    assert update_todo_response_data["title"] == todo_object.title
    assert update_todo_response_data["complete"] == todo_object.complete

    # Check the todo item is updated correctly on server side
    get_todo_response = send_get_todo(todo_object.id)
    assert get_todo_response.status_code == 200
    get_todo_data = get_todo_response.json()
    assert get_todo_data["id"] == todo_object.id
    assert get_todo_data["title"] == todo_object.title
    assert get_todo_data["complete"] == todo_object.complete

def test_delete_todo():    
    todo_object = test_create_todo()
    # Delete todo
    delete_todo_response = send_delete_todo(todo_object.id)
    assert delete_todo_response.status_code == 204


def generate_todo():
    return CreateTodo(title="New todo")

def send_create_todo( new_todo: CreateTodo) :
    return requests.post(ENDPOINT + "/todos", json=new_todo.dict())

def send_get_todo( id:int ):
    return requests.get(ENDPOINT + f"/todos/{id}")

def send_update_todo( todo: UpdateTodo ):
    return requests.put(ENDPOINT + f"/todos/{todo.id}", json=todo.dict())

def send_delete_todo( id:int ):
    return requests.delete(ENDPOINT + f"/todos/{id}")