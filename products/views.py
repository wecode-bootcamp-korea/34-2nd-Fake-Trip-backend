import pandas

from django.http                import JsonResponse
from django.views               import View
from django.db.models           import Q, Min, Avg, Count, IntegerField, Max
from django.db.models.functions import Coalesce

from products.models import Product, Room
from orders.models   import Reservation
from users.models    import Review

class ProductListView(View):
    def get(self, request):
        products = ['name', 'region', 'grade', 'check_in', 'start_date', 'end_date', 'check_out', 'start_date', 'end_date', 'rating', 'amanity']
        for product in products:
           globals()["{}".format(product)] = request.GET.get(product)

        price = request.GET.get('price', 0)
        sort        = request.GET.get('sort')
        offset      = int(request.GET.get('offset', 0))
        limit       = int(request.GET.get('limit', 100))
        
        q = Q()

        if name:
            q &= Q(name__contains = name)

        if region:
            q &= Q(region__name__contains = region)
        
        if grade:
            q &= Q(grade = grade)

        if price:
            q &= Q(room__price__gte = price)

        sort_set = {
            'random' : '?',
            'check_in-ascending' : 'check_in'
        }

        order_key = sort_set.get(sort, 'id')
        products = Product.objects.filter(q).order_by(order_key)[offset:offset+limit]

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
                'amanity' : [amanity.name for amanity in product.amenity.all()],
                'avg_rate' : product.review_set.aggregate(avg = Avg('rating'))['avg'],
                'min_price' : product.room_set.aggregate(min = Min('price',output_field=IntegerField()))['min']
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