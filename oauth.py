import os
from typing import Optional
from pydantic import BaseModel
from uuid import uuid4, UUID
from fastapi import APIRouter, Response, Depends, HTTPException
from utils import cookie, backend, SessionData, traq_base_path
import traq
from traq.api import oauth2_api
import requests
from requests import Response as ReqsResponse
import json



router = APIRouter()

client_id = os.getenv("CLIENT_ID", "jD70ycOCGcUfdTSmU6ORuAjVmSUYsJ4kyNxG")

class GetOAuthRedirectResponse(BaseModel):
    redirect_uri: str

@router.get("/redirect-uri", responses={200: {"model": GetOAuthRedirectResponse}}, operation_id="get_oauth_redirect_uri")
async def get_oauth_redirect(response: Response):
    """
    認証画面へリダイレクトするためのリダイレクト先のurlを返すAPI．
    このAPIを叩くとセッションが作られる
    """
    # 毎回新しいセッションを生成する (どうなんだろう...)
    session_id = uuid4()
    data = SessionData(access_token="")
    await backend.create(session_id, data)
    
    # クッキーにセッションIDを保持させる
    cookie.attach_to_response(response, session_id)

    # レスポンスボディ作成
    uri = f"{traq_base_path}/oauth2/authorize?response_type=code&client_id={client_id}"
    return GetOAuthRedirectResponse(redirect_uri=uri)


# traq apiを叩くための事前設定
configuration = traq.Configuration(
    host = traq_base_path
)

class TokenResponse(BaseModel):
    """
    post_o_auth2_token のレスポンスの型
    """
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: str
    id_token: Optional[str] = None


@router.get("/callback", status_code=204, responses={204:{"model":None}}, operation_id="get_oauth_callback")
async def get_oauth_callback(code: str,response: Response , session_id: UUID = Depends(cookie)):
    """
    認証画面を通過して得たcodeを用いてアクセストークンを得る
    """
    if session_id == None:
        print("cannot get session_id from cookie")
        raise HTTPException(status_code=400, detail="cookie is empty")

    # codeがない => 多分traqユーザーではない
    if code == "":
        raise HTTPException(status_code=400, detail="code is empty")
    
    api_response = None
    with traq.ApiClient(configuration) as api_client:
        api_instance = oauth2_api.Oauth2Api(api_client)
        # "authorization_code" で固定
        grant_type = "authorization_code"
        # code というクエリパラメータから得られる値 (必須)
        code = code
        try:
            # OAuth2 トークンエンドポイント, 今回は grant と code と client_id のみ必須
            api_response: TokenResponse = api_instance.post_o_auth2_token(grant_type=grant_type, code=code, client_id=client_id)
            if api_response.access_token == "":
                raise HTTPException(status_code=403, detail="invalid access token")
        
        except traq.ApiException as e:
            raise HTTPException(status_code=500, detail=f"Exception when calling Oauth2Api->post_o_auth2_token: {e}\n")
        
        # 一応バックエンドにアクセストークンを保存
        session_data = SessionData(access_token=api_response.access_token)
        await backend.update(session_id, session_data)

        # クッキーにセッションIDを貼り付ける
        cookie.attach_to_response(response, session_id)
    return None

class GetMeResponseFromTraq(BaseModel):
    """
    post_o_auth2_token のレスポンスの型
    """
    id: str
    name: str
    displayName: str
    iconFileId: str
    twitterId: str


async def auth_user(session_id: UUID) -> GetMeResponseFromTraq:
    """
    traQ user かどうか確かめる
    """
    # アクセストークンがセッションのデータに保持されているか確認するためにセッションデータを得る
    session_data = await backend.read(session_id=session_id)
    if not isinstance(session_data, SessionData):
        print(f"{session_data} is not instance of SessionData")
        raise HTTPException(status_code=401, detail="Your authentication is expierred or you have never been authenticated!")
    
    # 適切なアクセストークンがあるか確認する
    access_token = session_data.access_token
    if  access_token == "":
        raise HTTPException(status_code=401, detail="Token is empty")
    
    response: ReqsResponse = requests.get(url=f"{traq_base_path}/users/me",headers={"Authorization": f"Bearer {access_token}"})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error On Get Me From traQ")
    user: GetMeResponseFromTraq = response.json()
    return user

@router.get("/me", response_model=GetMeResponseFromTraq, operation_id="get_oauth_me")
async def get_oauth_me(session_id: UUID = Depends(cookie)):
    """
    認証が通らなかったら401が帰ってくる...はず
    """
    print("called")
    user = await auth_user(session_id)
    return user
