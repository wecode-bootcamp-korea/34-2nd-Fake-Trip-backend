import pandas
import boto3

from datetime import timedelta,datetime

from django.http                import JsonResponse, HttpResponse
from django.views               import View
from django.db.models           import Q, Min, Avg, Count, IntegerField, Max, Sum
from django.db.models.functions import Coalesce

from products.models       import Product, Room
from users.models          import Review
from orders.models         import Reservation
from core.token_validators import token_validator
from faketrip.settings     import AWS_S3_ACCESS_KEY_ID, AWS_S3_SECRET_ACCESS_KEY

class ProductListView(View):
    def get(self, request):
        products = ['name', 'region', 'grade', 'check_in', 'check_out']
        for product in products:
           globals()["{}".format(product)] = request.GET.get(product, None)

        price = request.GET.get('price', 0)
        sort   = request.GET.get('sort')
        offset = int(request.GET.get('offset', 0))
        limit  = int(request.GET.get('limit', 100))

        q = Q()

        if name:
            q &= Q(name = name)

        if region:
            q &= Q(region__name = region)

        if grade:
            q &= Q(grade = grade)

        if price:
            q &= Q(room__price__gte = int(price))

        sort_set = {
            'random' : '?',
            'check_in-ascending' : 'check_in',
            'price-asceding' : 'room__price',
        }

        order_key = sort_set.get(sort, 'id')
        
        products = Product.objects.filter(q).order_by(order_key)[offset:offset+limit]
        
        results = [{
                'id' : product.id,
                'name' : product.name,
                'grade' : product.grade,
                'address' : product.address,
                'region' : product.region.name,
                'check_in' : product.check_in,
                'check_out' : product.check_out,
                'category' : product.category.name,
                'main_image': product.productimage_set.get(is_main=1).url,
                'price' : {
                    'min_price' : product.room_set.aggregate(min = Min('price'))['min'],
                    'max_price' : product.room_set.aggregate(max = Max('price'))['max'],
                    'low_price' : product.room_set.filter(price__gte=price).aggregate(low_price = Min('price', output_field=IntegerField()))['low_price'],
                    'high_price' : product.room_set.filter(price__gte=price).aggregate(high_price = Max('price', output_field=IntegerField()))['high_price']
                }
            } for product in products
            ]
        return JsonResponse({'results' : results}, status = 200)

class ProductView(View):
    def get(self, request, product_id):
        start_date = request.GET.get('start_date')
        end_date   = request.GET.get('end_date')

        product = Product.objects.annotate(
            price        = Min(Coalesce('room__price',0),output_field=IntegerField()),
            rating       = Avg(Coalesce('review__rating',0)),
            rating_count = Count(Coalesce('review__id',0))
        ).prefetch_related('productimage_set', 'room_set','room_set__reservation_set').get(id = product_id)

        reservations       = Reservation.objects.filter(room__product = product)
        rooms              = Room.objects.filter(product = product)
        search_date        = set(pandas.date_range(start_date,end_date)[:-1])

        is_sold_out = True

        for room in rooms:
            for reservation in reservations:
                reservation_date = set(pandas.date_range(reservation.start_date,reservation.end_date)[:-1])
                if search_date & reservation_date:
                    room.quantity -= 1 
            if bool(room.quantity) == True:
                is_sold_out = False

        result = {
            'product_id'   : product.id,
            'name'         : product.name,
            'grade'        : product.grade,
            'address'      : product.address,
            'check_in'     : product.check_in,
            'check_out'    : product.check_out,
            'latitude'     : product.latitude,
            'longtitude'   : product.longtitude,
            'price'        : int(product.price) * len(search_date),
            'rating'       : product.rating,
            'rating_count' : product.rating_count,
            'images'       : [
                {
                    'url'     : image.url,
                    'is_main' : image.is_main
                }for image in product.productimage_set.all()
            ],
            'is_sold_out' : is_sold_out
        }

        return JsonResponse(result, status = 200)

class ReviewView(View):
    @token_validator
    def post(self, request, product_id):
        try:
            room_id      = request.POST.get('room_id')
            content      = request.POST.get('content')
            rating       = request.POST.get('rating')
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
    def delete(self, request, product_id):
        try:
            review_id = request.GET.get('review_id')
            review    = Review.objects.get(id = review_id)

            if review.user != request.user:
                return JsonResponse({'message' : 'Invalid Review'}, status = 400)

            if review.product_id != product_id:
                return JsonResponse({'message' : 'Invalid Review'}, status = 400)

            review.delete()

            return HttpResponse(status = 204)

        except Review.DoesNotExist:
            return JsonResponse({'message' : 'There Is No Review'}, status = 400)
        

