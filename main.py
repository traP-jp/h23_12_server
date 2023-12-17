import apis.oauth as oauth
import apis.dish as dish
from pydantic import BaseModel
from logging import getLogger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = getLogger("uvicorn.app")

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
def get_ping():
    return GetPingResponce(ping="pong")

app.include_router(oauth.router, prefix="/oauth", tags=["oauth"])
app.include_router(dish.router, prefix="/dish", tags=["dish"])