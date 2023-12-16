from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import oauth
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://localhost:4321",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GetPingResponce(BaseModel):
    ping: str

@app.get("/ping", response_model=GetPingResponce, operation_id="get_ping")
def get_ping(iserror: int = None):
    if iserror != None:
        raise HTTPException(status_code=416, detail="I'm tea pod")
    return GetPingResponce(ping="pong")


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

app.include_router(oauth.router, prefix="/oauth", tags=["oauth"])