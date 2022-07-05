import requests

class Kakao_Token_Error(Exception):
    def __init__(self):
        self.message = 'Invalid Token'

class KakaoAPI:
    def __init__(self, access_token):
        self.access_token = access_token
        self.user_url     = "https://kapi.kakao.com/v2/user/me"

    def get_kakao_user_information(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}

        response = requests.get(self.user_url, headers = headers, timeout = 3)
        
        if not response.status_code == 200:
            raise Kakao_Token_Error
	
        return response.json()

