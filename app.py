import fastapi
from fastapi import BackgroundTasks, FastAPI, Request, Response, HTTPException, Query
from config import *
app = FastAPI()

# Verify facebook messenger subcription
def verify_token(hub_mode, hub_challenge, hub_verify_token):
    if hub_verify_token == META_VERIFY_TOKEN and hub_mode == 'subscribe':
        return int(hub_challenge)
    # Return Error 404 not found
    raise HTTPException(status_code=404, detail="Not found")

# Setup a client to send requests
@app.get("/")
async def index(request: Request):
    query_params = request.query_params
    hub_mode = query_params.get("hub.mode")
    hub_challenge = query_params.get("hub.challenge")
    hub_verify_token = query_params.get("hub.verify_token")
    return verify_token(hub_mode, hub_challenge, hub_verify_token)
