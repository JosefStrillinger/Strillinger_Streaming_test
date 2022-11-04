import datetime
import json
import os
from flask import Flask, request,jsonify
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename
import sqlite3
from sqlalchemy.sql.expression import func

from sqlalchemy import Column, Integer, Text, DateTime, create_engine, LargeBinary
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pathlib import Path

from dataclasses import dataclass

ALLOWED_EXTENSIONS = {'mp3', 'wav'}

app = Flask(__name__)
api = Api(app)

Base = declarative_base()
metadata = Base.metadata
engine = create_engine(r'sqlite:///D:\Apps\SQLite\musicinfo.sqlite3')
db_session = scoped_session(sessionmaker(autocommit=True, autoflush=True, bind=engine))
Base.query = db_session.query_property


def getMusicInfoLocal():
    id = 1
    music = []
    for x in os.listdir():#Kann auch anderen Path eintragen, vllt wenn auf Raspberry, umändern
        if x.endswith('.mp3'):#vllt allowed_extensions
            m = MusicInfo(id, x, Path(x).resolve())
            music.append(m)
            id+=1
        if x.endswith('.wav'):
            m = MusicInfo(id, x, Path(x).resolve())
            music.append(m)
            id+=1
    return music


def getMusicInfo(music):
    id = 1
    musicInfos=[]
    for x in music:  # Kann auch anderen Path eintragen, vllt wenn auf Raspberry, umändern
        m = MusicInfo(id, x, "path")
        musicInfos.append(m)
        id += 1
    return musicInfos
            

class MusicInfo(Base):
    __tablename__ = 'musicinfo'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    path = Column(Text, nullable=False)
    
    def __init__(self, id, name, path):
        self.id = id
        self.name = name
        self.path = path
    
    def serialize(self):
        return{
            "ID" : str(self.ID),
            "NAME" : self.name,
            "PATH" : self.PATH
        }
  
class SongInfo:
    def __init__(self, id, name, path):
        self.id = id
        self.name = name
        self.path = path
        
    def __str__(self):
        return str(self.id)+" | "+self.name+" | "+self.path
    
    def serialize(self):
        return {"id": self.id, "name":self.name, "path":self.path}
    
class Service(Resource):
    def get(self, id):
        music = MusicInfo.query.get(id)
        if not music:
            return jsonify({"message" : "does not exist"})
        return music.serialize()
    
    def put(self, id):
        data = request.get_json(force=True)['info']
        info=MusicInfo(name=data['name'], path=data['path'])
        db_session.add(info)
        db_session.flush()
        return jsonify(info)
        
    def delete(self, id):
        music = MusicInfo.query.get(id)
        if not music:
            return jsonify({"message" : "file with this id does not exist %s" %id})
        db_session.delete(music)
        db_session.flush()
        return jsonify(music)
        
    def getByName(self, name):
        music = MusicInfo.query.get(name)
        if not music:
            return jsonify({"message" : "does not exist"})
        return music.serialize()
    
    def patch(self, id):
        music = MusicInfo.query.get(id)
        if music is None:
            return jsonify({'message': 'object with id %d does not exist'%id})
        data = json.loads(request.json['info'])
        if 'name' in data:
            music.name = data['name']
        if 'path' in data:
            music.path = data['path']
        db_session.add(music)
        db_session.flush()
        return jsonify({'message':'object with id %d modified'%id})
    
    
api.add_resource(Service, "/file/<string:id>")

def createDB():
    Base.metadata.create_all(bind = engine)
   
class AllMusic(Resource):
    def get(self):
        return {"Result" : "blablablablabla"}
           
#TODO: 
 
# if __name__ == '__main__':
#     createDB()
#     app.run(debug=True, host="0.0.0.0")


            