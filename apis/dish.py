from fastapi import APIRouter, Response

router = APIRouter()

@router.get("/{id}",responses = {200: {"content": {"image/png": {}}}}, response_class=Response, operation_id="get_dish")
def get_dish_image(id: int):
    with open("./notion-asm-icon.png", "rb") as img:
        b = img.read()
    return Response(content=b, media_type="image/png")