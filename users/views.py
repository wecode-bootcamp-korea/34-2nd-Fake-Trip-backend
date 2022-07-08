import jwt
import boto3

from django.views import View
from django.http  import JsonResponse, HttpResponse
from datetime     import datetime

from users.models          import User, Review
from faketrip.settings     import SECRET_KEY, ALGORITHM, AWS_S3_ACCESS_KEY_ID, AWS_S3_SECRET_ACCESS_KEY
from core.social_apis      import Kakao_Token_Error, KakaoAPI
from core.token_validators import token_validator

class SigninView(View):
    def get(self, request):
        try:
            access_token     = request.headers.get('Authorization')
            user_information = KakaoAPI(access_token).get_kakao_user_information()
            
            kakao_pk = user_information.get('id')
            email    = user_information.get('kakao_account').get('email')
            nickname = user_information.get('properties').get('nickname')

            user, created = User.objects.get_or_create(kakao_pk=kakao_pk, defaults = {"email" : email, "name" : nickname, 'phone_number' : None})
            
            if not created and not(user.email == email and user.name == nickname):
                user.email, user.name = email, nickname
                user.save()

            authorization = jwt.encode({'user_id' : user.id}, SECRET_KEY, ALGORITHM)

            return JsonResponse({'message' : 'SUCCESS'},headers = {'Authorization' : authorization}, status = 200)
        
        except Kakao_Token_Error as error:
            return JsonResponse({'message' : error.message}, status = 401)

class ReviewView(View):
    @token_validator
    def post(self, request):
        try:
            room_id      = request.POST.get('room_id')
            content      = request.POST.get('content')
            rating       = request.POST.get('rating')
            product_id   = request.POST.get('product_id')
            review_image = request.FILES.get('review_image')
            image_url    = None

            if not rating:
                return JsonResponse({'message' : 'Choice Rating'}, status = 400)

            if not content:
                return JsonResponse({'message' : 'Insert Content'}, status = 400)
            
            if review_image:
                image_time = (str(datetime.now())).replace(" ","") 
                image_type = (review_image.content_type).split("/")[1]

                s3_client = boto3.client(
                    's3',
                    aws_access_key_id     = AWS_S3_ACCESS_KEY_ID,
                    aws_secret_access_key = AWS_S3_SECRET_ACCESS_KEY
                )

                s3_client.upload_fileobj(
                    review_image,
                    "ding-s3-bucket",
                    image_time+"."+image_type,
                    ExtraArgs = {
                        "ContentType" : review_image.content_type
                    }
                )

                image_url = "http://dkinterest.s3.ap-northeast-2.amazonaws.com/"+image_time+"."+image_type
                image_url = image_url.replace(" ","/")

            Review.objects.create(
                user       = request.user,
                product_id = product_id,
                room_id    = room_id,
                content    = content,
                rating     = rating,
                image_url  = image_url
            )

            return JsonResponse({'message' : 'Create Review'}, status = 201)

        except IndexError:
            return JsonResponse({'message' : 'Index Error'}, status = 400)

    @token_validator
    def delete(self, request):
        try:
            review_id  = request.GET.get('review_id')
            product_id = request.GET.get('product_id')
            review     = Review.objects.get(id = review_id)

            if review.user != request.user:
                return JsonResponse({'message' : 'Invalid Review'}, status = 400)

            if review.product_id != int(product_id):
                return JsonResponse({'message' : 'Invalid Review'}, status = 400)

            review.delete()
            
            return HttpResponse(status = 204)

        except Review.DoesNotExist:
            return JsonResponse({'message' : 'There Is No Review'}, status = 400)
