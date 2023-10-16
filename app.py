import fastapi
from fastapi import BackgroundTasks, FastAPI, Request, Response, HTTPException, Query

app = FastAPI()

# Setup a client to send requests
