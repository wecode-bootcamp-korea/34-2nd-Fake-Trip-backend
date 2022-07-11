import requests

import jwt

from django.views import View
from django.http  import JsonResponse

from users.models      import User
from faketrip.settings import SECRET_KEY, ALGORITHM
from core.social_apis  import Kakao_Token_Error, KakaoAPI
from core.validators   import validate_phone_number

class SigninView(View):
    def get(self, request):
        try:
            access_token     = request.headers.get('Authorization')
            user_information = KakaoAPI(access_token).get_kakao_user_information()
            
            kakao_pk      = user_information.get('id')
            email         = user_information.get('kakao_account').get('email')
            nickname      = user_information.get('properties').get('nickname')
            phone_number = user_information.get('properties').get('phone_numeber')

            user, created = User.objects.get_or_create(kakao_pk=kakao_pk, defaults = {"email" : email, "name" : nickname, 'phone_number' : phone_number})
            
            if not created and not(user.email == email and user.name == nickname):
                user.email, user.name = email, nickname
                user.save()

            authorization = jwt.encode({'user_id' : user.id}, SECRET_KEY, ALGORITHM)

            return JsonResponse({'message' : 'SUCCESS'},headers = {'Authorization' : authorization}, status = 200)
        
        except Kakao_Token_Error as error:
            return JsonResponse({'message' : error.message}, status = 401)

class UserView(View):
    @token_validator
    def patch(self, request):
        try:
            phone_number = request.body.get(phone_number)

            validate_phone_number(phone_number)

            request.user.phone_number = phone_number
            request.user.save()

            return JsonResponse({'message' : 'SUCCES'}, status = 200)

        except ValidationError as e:
            return JsonResponse({'message' : e.message}, status = 400) 