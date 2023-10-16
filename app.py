import fastapi, traceback
from fastapi import BackgroundTasks, FastAPI, Request, Response, HTTPException, Query
from config import *
import sqlite3, httpx
app = FastAPI()

client = httpx.AsyncClient()

db = sqlite3.connect('database.db', check_same_thread=False)
cursor = db.cursor()

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

# Get POST request from Facebook Messenger API
@app.post("/")
async def index(request: Request):
    # Get JSON content of a request
    # Handling error:
    try:
        output = await request.json()
        page_id = ""
        for event in output['entry']:
            # Please read documentation of Facebook Messenger API to understand this part
            if event.get('messaging'):
                messaging = event['messaging']
                for message in messaging:
                    if message.get('message'):
                        page_id = message['recipient']['id']
                    elif message.get('postback'):
                        page_id = message['recipient']['id']
                    else:
                        pass
        try:
            url = cursor.execute("SELECT url FROM callback WHERE page_id = ?", (page_id,)).fetchone()[0]
            await client.post(url, json=output)
            return Response(status_code=200, content="EVENT_RECEIVED")
        except Exception as e:
            with open('errlog.txt', 'a') as f:
                f.write(str(e) + '\n')
                f.write(str(traceback.format_exc()) + '\n\n\n')
    # If there is an error, log it to errlog.txt with trace
    except Exception as e:
        with open('errlog.txt', 'a') as f:
            f.write(str(e) + '\n')
            f.write(str(traceback.format_exc()) + '\n\n\n')
        # Return error with status 400
        return Response(status_code=200, content="Invalid JSON")
    # Return status 200
    return Response(status_code=200, content="EVENT_RECEIVED")

# Return url of a page_id
@app.get("/get")
async def get(request: Request):
    # Get query params
    query_params = request.query_params
    page_id = query_params.get("page_id")
    # Handling error:
    try:
        url = cursor.execute("SELECT url FROM callback WHERE page_id = ?", (page_id,)).fetchone()[0]
        return Response(status_code=200, content=url)
    # If there is an error, log it to errlog.txt with trace
    except Exception as e:
        with open('errlog.txt', 'a') as f:
            f.write(str(e) + '\n')
            f.write(str(traceback.format_exc()) + '\n\n\n')
        # Return error with status 400
        return Response(status_code=400, content="Invalid page_id")

@app.post("/update")
async def update(request: Request):
    # Get the params of the request
    try:
        query_params = request.query_params
        page_id = query_params.get("page_id")
        url = query_params.get("url")
        # Remove beginning and ending spaces
        url = url.strip()
        # Check if url is ssl or not
        if not url.startswith('https://'):
            raise Exception("A secure callback URL (https) is required.")
        if not page_id or not url:
            raise Exception("Missing page_id or url")
        if not cursor.execute("SELECT * FROM callback WHERE page_id = ?", (page_id,)).fetchone():
            cursor.execute("INSERT INTO callback VALUES (?, ?)", (page_id, url))
        else:
            cursor.execute("UPDATE callback SET url = ? WHERE page_id = ?", (url, page_id))
        db.commit()
        return Response(status_code=200, content="Updated")
    # If there is an error, log it to errlog.txt with trace
    except Exception as e:
        with open('errlog.txt', 'a') as f:
            f.write(str(e) + '\n')
            f.write(str(traceback.format_exc()) + '\n\n\n')
        # Return error with status 400
        return Response(status_code=400, content=str(e))