import os
import json
import shutil
import urllib.request
import tarfile
import aiofiles
from typing import Optional
from utils import get_gh_token
from github import Github
from fastapi import FastAPI, File, Form, HTTPException
from pydantic import BaseModel
from tensorflow.keras.models import load_model

app = FastAPI(title='이미지 분류 API', version='0.1')
models = {}

class Model(BaseModel):
   name: str = "flower-classifier"
   version: str = "latest"
   desc: Optional[str] = None
   url: Optional[str] = None

def _get_model_info(model_name='flower-classifier', version=None):
    g = Github(get_gh_token())
    repo = g.get_repo("books-by-chansung/mh-mlops-model")

    if version == None:
        release = repo.get_latest_release()
        version = release.tag_name
    else:
        release = repo.get_release(version)
    
    url = release.get_assets()[0].browser_download_url
    desc = release.body

    return Model(name=model_name, 
                 version=version, 
                 desc=desc,
                 url=url)

def _get_model(model_name='flower-classifier', version=None, force=False):
    model = _get_model_info('flower', version)
    
    model_path = f'{model.model_name}/{model.version}'
    model_file = f'{model_path}/{model.model_name}.tar.gz'

    if force and os.path.isdir(model_path):
        shutil.rmtree(model_path)    

    if not os.path.isdir(model_path):
        os.makedirs(model_path, exist_ok=False)
        urllib.request.urlretrieve(model.url, model_file)

        tar = tarfile.open(model_file)
        tar.extractall(model_path)
        tar.close()

        os.remove(model_file)
    
    return model, f'{model_path}/{model_name}'

@app.on_event("startup")
def load_modules():
    print("Get latest model initially...")
    model_name = "flower-classifier"
    model, cur_model_path = _get_model(model_name=model_name, force=False)
    print("Done latest model initially...")
    
    if model_name not in models:
        models[model_name] = {}
    
    print("Load the latest model initially...")    
    models[model_name]["latest"] = (model, cur_model_path, load_model(cur_model_path))
    print("Load the latest model initially...")
    

@app.get("/")
def hello():
    return {"메시지": "헬로 FastAPI"}

@app.get("/models/info")
def get_model_info(model: Model):
    model, _, _ = models[model.model_name][model.version]
    return model.desc

@app.get("/models/labels")
async def get_model_label(model: Model):
    _, path, _ = models[model.model_name][model.version]
    label_file_path = f'{path}/assets/labels.txt'
    
    async with aiofiles.open(label_file_path) as f:
        content = await f.read()
        labels = content.split('\n')
        
    return {"labels": labels}
    