from uuid import uuid4
from fastapi import APIRouter, Response, Depends, HTTPException
from sessionstore import cookie, backend, session_verifier ,SessionData
import secrets
import os
import traq
from traq.api import oauth2_api
from traq.model.o_auth2_token import OAuth2Token
from pprint import pprint
from pydantic import BaseModel

router = APIRouter()

traq_base_path = "https://q.trap.jp/api/v3"

client_id = os.getenv("CLIENT_ID", "jD70ycOCGcUfdTSmU6ORuAjVmSUYsJ4kyNxG")

@router.get("/redirect-uri")
async def get_oauth_redirect(response: Response):

    # セッションIDを生成
    session_id = uuid4()
    verifier = secrets.token_hex(32)
    data = SessionData(verifier=verifier, accessToken=None)


    await backend.create(session_id, data)
    cookie.attach_to_response(response, session_id)
    uri = f"{traq_base_path}/oauth2/authorize?response_type=code&client_id={client_id}"

    return {"redirect_uri": uri}


# post_o_auth2_token のレスポンスの型
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str
    id_token: str

# traq apiを叩くための事前設定
configuration = traq.Configuration(
    host = traq_base_path
)

@router.get("/callback", dependencies=[Depends(cookie)])
async def get_oauth_callback(code: str,response: Response , session_id: uuid4 = Depends(session_verifier)):
    if code == "":
        raise HTTPException(status_code=400, detail="code is empty")
    api_response: TokenResponse = None

    with traq.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = oauth2_api.Oauth2Api(api_client)
        # "authorization_code" で固定
        grant_type = "authorization_code"
        # code というクエリパラメータから得られる値 (必須)
        code = code

        # example passing only required values which don't have defaults set
        # and optional values
        try:
            # OAuth2 トークンエンドポイント
            api_response = api_instance.post_o_auth2_token(grant_type, code=code, client_id=client_id)
            if len(api_response.access_token) == 0:
                raise HTTPException(status_code=400, detail="Bad Request\n")
        except traq.ApiException as e:
            raise HTTPException(status_code=500, detail=f"Exception when calling Oauth2Api->post_o_auth2_token: {e}\n")
        
        # 一応バックエンドにアクセストークンを保存
        session_data: SessionData = backend.read(session_id)
        session_data.accessToken = api_response.access_token
        await backend.update(session_id, session_data)

        # クッキーにセッションIDを貼り付ける
        cookie.attach_to_response(response, session_id)
    return {"access_token": api_response.access_token}

@router.get("/access-token", dependencies=[Depends(cookie)])
async def get_access_token(session_data: SessionData = Depends(session_verifier)):
    return {"verifier": session_data.verifier, "access_token": session_data.accessToken}