import os
import shutil
import urllib.request
import tarfile
from utils import get_gh_token
from github import Github
from fastapi import FastAPI

app = FastAPI(title='이미지 분류 API', version='0.1')

def get_model_info(model_name='flower', version=None):
    g = Github(get_gh_token())
    repo = g.get_repo("books-by-chansung/mh-mlops-model")

    if version == None:
        release = repo.get_latest_release()
        version = release.tag_name
    else:
        release = repo.get_release(version)
    
    url = release.get_assets()[0].browser_download_url
    desc = release.body

    return version, url, desc

def get_model(model_name='flower-classifier', version=None, force=False):
    version, url, desc = get_model_info('flower', version)
    print(version)
    print(url)
    print(desc)
    
    model_path = f'{model_name}/{version}'
    model_file = f'{model_path}/{model_name}.tar.gz'

    if not os.path.isdir(model_path) or force:
        shutil.rmtree(model_path)

        os.makedirs(model_path, exist_ok=False)
        urllib.request.urlretrieve(url, model_file)

        tar = tarfile.open(model_file)
        tar.extractall(model_path)
        tar.close()

        os.remove(model_file)
    
    return version, desc, f'{model_path}/{model_name}'

@app.on_event("startup")
def load_modules():
    cur_version, cur_desc, cur_model_path = get_model(force=True)

@app.get("/")
def hello():
    return {"메시지": "헬로 FastAPI"}

# @app.get("/clssify/{model_name}/labels")
# def labels():
#     with open('labels.txt') as f:
#         content = f.read()
#         labels = content.split('\n')

#     return {"labels": labels}

# @app.get("/clssify/{model_name}/info")
# def model_info():
