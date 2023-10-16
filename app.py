import fastapi
from fastapi import BackgroundTasks, FastAPI, Request, Response, HTTPException, Query

app = FastAPI()

# Setup a client to send requests
@app.get("/test")
async def root():
    print("test hosting")
    return {"message": "Hello World Test"}
