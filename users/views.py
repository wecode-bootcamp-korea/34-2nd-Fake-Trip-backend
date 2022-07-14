import jwt
import boto3

from django.views           import View
from django.http            import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError

from users.models            import User, Review
from faketrip.settings       import SECRET_KEY, ALGORITHM, AWS_S3_ACCESS_KEY_ID, AWS_S3_SECRET_ACCESS_KEY
from core.social_apis        import Kakao_Token_Error, KakaoAPI
from core.token_validators   import token_validator
from core.file_upload_module import FileHandler, AwsUploader
from core.validators         import validate_phone_number

class SigninView(View):
    def get(self, request):
        try:
            access_token     = request.headers.get('Authorization')
            user_information = KakaoAPI(access_token).get_kakao_user_information()
            
            kakao_pk      = user_information.get('id')
            email         = user_information.get('kakao_account').get('email')
            nickname      = user_information.get('properties').get('nickname')
            phone_number = user_information.get('properties').get('phone_numeber')

            user, created = User.objects.get_or_create(kakao_pk=kakao_pk, defaults = {"email" : email, "name" : nickname, 'phone_number' : None})
            
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


aws_keys = {'aws_access_key_id'     : AWS_S3_ACCESS_KEY_ID,
            'aws_secret_access_key' : AWS_S3_SECRET_ACCESS_KEY}
config   = {'bucket_name' : "ding-s3-bucket"}

file_uploader = AwsUploader(boto3.client('s3',**aws_keys), config)
file_handler  = FileHandler(file_uploader)

class ReviewView(View):
    @token_validator
    def post(self, request):
        product_id   = request.POST.get('product_id')
        room_id      = request.POST.get('room_id')
        content      = request.POST.get('content')
        rating       = request.POST.get('rating')
        product_id   = request.POST.get('product_id')
        review_image = request.FILES.get('image')

        if not rating:
            return JsonResponse({'message' : 'Choice Rating'}, status = 400)

        if not content:
            return JsonResponse({'message' : 'Insert Content'}, status = 400)

        image_url     = file_handler.upload(review_image)

        Review.objects.create(
            user       = request.user,
            product_id = product_id,
            room_id    = room_id,
            content    = content,
            rating     = rating,
            image_url  = image_url
        )

        return JsonResponse({'message' : 'Create Review'}, status = 201)
    
    @token_validator
    def delete(self, request):
        try:
            review_id = request.GET.get('review_id')
            file_url  = Review.objects.get(id = review_id).image_url

            file_handler.delete(file_url)

            return HttpResponse(status = 204)

        except Review.DoesNotExist:
            return JsonResponse({'message' : 'Invalid Review'}, status = 400)