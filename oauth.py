from uuid import uuid4
from fastapi import APIRouter, Response, Depends, HTTPException
from sessionstore import cookie, backend, session_verifier ,SessionData
import hashlib
import base64
import secrets
import os
import traq
from traq.api import oauth2_api
from traq.model.o_auth2_token import OAuth2Token
from pprint import pprint

router = APIRouter()

traq_base_path = "https://q.trap.jp/api/v3"

client_id = os.getenv("CLIENT_ID", "jD70ycOCGcUfdTSmU6ORuAjVmSUYsJ4kyNxG")

@router.get("/redirect-uri")
async def get_oauth_redirect(response: Response):

    # セッションIDを生成
    session = uuid4()
    verifier = secrets.token_hex(32)
    data = SessionData(verifier=verifier, accessToken=None)


    await backend.create(session, data)
    cookie.attach_to_response(response, session)
    uri = f"{traq_base_path}/oauth2/authorize?response_type=code&client_id={client_id}"

    return {"redirect_uri": uri}


# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure OAuth2 access token for authorization: OAuth2
configuration = traq.Configuration(
    host = "https://q.trap.jp/api/v3"
)

@router.get("/callback", dependencies=[Depends(cookie)])
async def get_oauth_callback(code: str, session_data: SessionData = Depends(session_verifier)):
    if code == "":
        raise HTTPException(status_code=400, detail="code is empty")
    api_response = None
    # Enter a context with an instance of the API client
    with traq.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = oauth2_api.Oauth2Api(api_client)
        grant_type = "authorization_code" # str | 
        code = code # str |  (optional)

        # example passing only required values which don't have defaults set
        # and optional values
        try:
            # OAuth2 トークンエンドポイント
            api_response = api_instance.post_o_auth2_token(grant_type, code=code, client_id=client_id)
            pprint(api_response)
        except traq.ApiException as e:
            print("Exception when calling Oauth2Api->post_o_auth2_token: %s\n" % e)

    return {"responce": str(api_response)}

@router.get("/access-token", dependencies=[Depends(cookie)])
async def get_access_token(session_data: SessionData = Depends(session_verifier)):
    return {"verifier": session_data.verifier, "access_token": session_data.accessToken}