import pandas
import json
from datetime import datetime

from django.http                import JsonResponse
from django.views               import View
from django.db.models           import Q
from django.db.models           import Q, Min, Avg, Count, IntegerField, Max
from django.db.models.functions import Coalesce
from datetime                   import datetime, timedelta

from django.http                import JsonResponse
from django.views               import View
from django.db.models           import Q, Min, Avg, Count, IntegerField, Max
from django.db.models.functions import Coalesce

from products.models import Product, Room, Amenity
from orders.models   import Reservation
from users.models    import Review

class ProductListView(View):
    def get(self, request):
        products = ['name', 'region', 'grade', 'rating', 'sort', 'search', 'guest', 'category']
        for product in products:
           globals()["{}".format(product)] = request.GET.get(product)

        amenity    = request.GET.getlist('amenity')
        guest      = request.GET.get('guest',0)
        start_date = request.GET.get('start_date',0)
        end_date   = request.GET.get('end_date',1000000)
        min_price  = request.GET.get('min_price',0)
        max_price  = request.GET.get('max_price',1000000)
        offset     = int(request.GET.get('offset', 0))
        limit      = int(request.GET.get('limit', 10))

        def rooms_full(product,start_date,end_date):
            reservations = Reservation.objects.filter(room__product = product) 
            rooms        = Room.objects.filter(product = product)   
            search_date  = set(pandas.date_range(start_date,end_date)[:-1]) 
            is_sold_out  = []

            for room in rooms:
                for reservation in room.reservation_set.all().filter(room__price__range=[min_price,max_price]).filter(room__max_guest__gte=guest):
                    reservation_date = set(pandas.date_range(reservation.start_date,reservation.end_date)[:-1])
                    if search_date & reservation_date:
                        room.quantity -= 1 
                        if bool(room.quantity) == False:
                            is_sold_out.append(reservation.room_id)
            return is_sold_out

        def room_min_price(product, min_price, max_price, guest, start_date, end_date):
            min_price = product.room_set.filter(price__range=[min_price,max_price]).filter(max_guest__gte=guest).exclude(id__in=rooms_full(product,start_date,end_date)).aggregate(min = Min('price',output_field=IntegerField()))['min']
            return min_price

        def product_amenity(product, amenity):
            a=0
            if amenity != []:
                for j in amenity:
                    if j in [i.name for i in product.amenity.all()]:
                        a += 1
                    if a == len(amenity):
                        return [i.name for i in product.amenity.all()]
            else:
                return [amenity.name for amenity in product.amenity.all()]
                
        q = Q()

        if search:
            q &= (Q(name__contains = search) | Q(region__name__contains = search))

        FILTER_SET = {
            'region'  : 'region__name',
            'amenity' : 'amenity__name',
            'grade'   : 'grade__gte',
            'guest'   : 'room__max_guest__gte',
            '[min_price,max_price]' : 'room__price__range',
            'category' : 'category__name'
            }
        SORT_SET = {
            'random' : '?',
            'check_in-ascending' : 'check_in'
        }

        filter = { FILTER_SET.get(key) : value for key, value in request.GET.items() if FILTER_SET.get(key) }
        order_key = SORT_SET.get(sort, 'id')

        products = Product.objects.filter(**filter).filter(q).order_by(order_key).distinct()

        results = [
            {
                'id' : product.id,
                'name' : product.name,
                'grade' : product.grade,
                'address' : product.address,
                'region' : product.region.name,
                'check_in' : product.check_in,
                'check_out' : product.check_out,
                'latitude' : product.latitude,
                'longtitude' : product.longtitude,
                'category' : product.category.name,
                'main_image': product.productimage_set.get(is_main=1).url,
                'amenity' : [amenity.name for amenity in product.amenity.all()],
                'avg_rate' : product.review_set.aggregate(avg = Avg('rating'))['avg'],
                'price' : 
                    {'default' : product.room_set.aggregate(min = Min('price',output_field=IntegerField()))['min'],
                    'min_price' : room_min_price(product, min_price, max_price, guest, start_date, end_date)
                    }
            } for product in products if room_min_price(product, min_price, max_price, guest, start_date, end_date) != None and product_amenity(product, amenity) != None
            ][offset:offset+limit]
        return JsonResponse({'results' : results}, status = 200)

class ProductView(View):
    def get(self, request, product_id):
        try:
            start_date = request.GET.get('start_date')
            end_date   = request.GET.get('end_date')

            product = Product.objects.annotate(
                rating       = Coalesce(Avg('review__rating'),0.0),
                review_count = Coalesce(Count('review__id'),0)
            ).get(id = product_id)

            product_price =  Product.objects.aggregate(price = Coalesce(Min('room__price'),0,output_field = IntegerField()))['price']

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
                'id'           : product.id,
                'name'         : product.name,
                'grade'        : product.grade if product.grade else 0,
                'address'      : product.address,
                'check_in'     : product.check_in,
                'check_out'    : product.check_out,
                'latitude'     : product.latitude,
                'longtitude'   : product.longtitude,
                'price'        : product_price * len(search_date),
                'rating'       : product.rating,
                'review_count' : product.review_count,
                'images'       : [
                    {
                        'url'     : image.url,
                        'is_main' : image.is_main
                    }for image in product.productimage_set.all()
                ],
                'is_sold_out' : is_sold_out
            }

            return JsonResponse(result, status = 200)
        
        except Product.DoesNotExist:
            return JsonResponse({'message' : 'Invalid Product'}, status = 400)

class ReviewsView(View):
    def get(self, request, product_id):
        sort_key   = request.GET.get('sort', 'newest')
        rating     = request.GET.get('rating')
        has_image  = request.GET.get('has_image')
        offset     = request.GET.get('offset', 0)
        limit      = request.GET.get('limit', 10)

        sort_dict = {
            'newest'      : '-updated_at',
            'random'      : '?',
            'low_rating'  : 'rating',
            'high_rating' : '-rating'
        }

        q = Q(product_id = product_id)

        if rating:
            q &= Q(rating__exact = rating)

        if has_image:
            q &= Q(image_url__isnull = False)

        reviews = Review.objects.filter(q).order_by(sort_dict.get(sort_key))[offset:offset + limit]

        result = [
            {   
                'id'         : review.id,
                'product_id' : review.product_id,
                'user_name'  : review.user.name,
                'rating'     : review.rating,
                'content'    : review.content,
                'image_url'  : review.image_url,
                'updated_at' : review.updated_at.date(),
            }for review in reviews
        ]

        return JsonResponse({'reviews' : result}, status = 200)


class RoomsView(View):
    def get(self, request, product_id):
        start_date = request.GET.get('start_date', datetime.now().strftime("%Y-%m-%d"))
        end_date   = request.GET.get('end_date')
        guests     = int(request.GET.get('guests',2))
        
        if not end_date:
            join_date = datetime.now()+ timedelta(days=1)
            end_date  = join_date.strftime("%Y-%m-%d")
        
        search_date = set(pandas.date_range(start_date,end_date)[:-1])
        
        q = Q(product_id = product_id)

        q &= Q(max_guest__gte = guests)

        rooms = Room.objects.filter(q).prefetch_related('reservation_set')

        list1 = []
        
        for room in rooms:
            for reservation in room.reservation_set.all():
                reservation_date  = set(pandas.date_range(reservation.start_date,reservation.end_date)[:-1])        
                if search_date & reservation_date:
                    room.quantity -= 1
                    if not room.quantity:
                        list1.append(room.id)

        p &= Q(id__in = list1)

        rooms = Room.objects.filter(q).exclude(p).order_by('price').prefetch_related('roomimage_set')

        rooms_result = [
            {
                'id'         : room.id,
                'name'       : room.name,
                'price'      : int(room.price) * len(search_date),
                'min_guests' : room.min_guest,
                'max_guests' : room.max_guest,
                'size'       : room.size,
                'images'     : [
                    {
                        'id'      : image.id,
                        'url'     : image.url,
                        'is_main' : image.is_main
                    }for image in room.roomimage_set.order_by('is_main')
                ]
            }for room in rooms]

        return JsonResponse({'rooms' : rooms_result}, status = 200)