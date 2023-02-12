from cgitb import reset
import re
from typing import Optional
from fastapi import FastAPI
import pymongo 
from pydantic import BaseModel, Field
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware



client = pymongo.MongoClient('mongodb://localhost:27017')
db = client["todo"]["tasks"]


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")
    

        








class Task(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: Optional[str]
    done: Optional[bool] = False
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True #required for the _id 
        json_encoders = {ObjectId: str}
@app.get('/items')
def index():
    return [Task(**task) for task in db.find()]

class CreateTask(BaseModel):
    title: str
    done: Optional[bool] = False
    
@app.post('/items/create')
def create(task: CreateTask):
    result  = db.insert_one({'title': task.title, 'done': task.done})
    return {'_id': str(result.inserted_id), 'title': task.title, 'done': task.done}



class UpdateTask(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: Optional[str] = None
    done: Optional[bool] = None
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True #required for the _id 
        json_encoders = {ObjectId: str}
        
@app.post('/items/update')
def update(task: UpdateTask):
    if task.title is not None: result = db.update_one({'_id': ObjectId(task.id)}, {'$set': {'title': task.title}})
    if task.done is not None:result = db.update_one({'_id': ObjectId(task.id)}, {'$set': {'done': task.done}})
    return Task(**db.find_one({'_id': ObjectId(task.id)}) )

class DeleteTask(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
@app.post('/items/delete', status_code=204)
def delete(data:DeleteTask):
    result = db.delete_one({'_id': data.id})
    # return code 204
    





class UpdateTaskRequest(BaseModel):
    
    title: str = Optional[str]
    done: bool = Optional[bool]






