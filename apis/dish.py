from fastapi import APIRouter, Response
from pydantic import BaseModel, Base64Bytes
import base64

router = APIRouter()

class ImageResponse(BaseModel):
    base64_bytes: Base64Bytes

@router.get("/{id}",responses = {200: {"model": ImageResponse}}, response_model=ImageResponse, operation_id="get_dish")
def get_dish_image(id: int):
    with open("./notion-asm-icon.png", "rb") as img:
        b = img.read()
        byte_data = base64.b64encode(b)
    return ImageResponse(base64_bytes=byte_data)