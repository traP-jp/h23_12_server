from fastapi import FastAPI
import oauth

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "world"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

app.include_router(oauth.router, prefix="/oauth", tags=["oauth"])