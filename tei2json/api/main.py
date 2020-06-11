from fastapi import FastAPI
import json
app = FastAPI()

with open('../output/data.json') as json_file:
    data = json.load(json_file)
    
@app.get("/")
def read_root():
    return { "data": data }