import pandas

from datetime import timedelta

from django.http                import JsonResponse
from django.views               import View
from django.db.models           import Q, F, Min, Avg, Count, IntegerField, Max, Sum
from django.db.models.functions import Coalesce

from products.models import Product, Room
from orders.models   import Reservation

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
        try:
            start_date = request.GET.get('start_date')
            end_date   = request.GET.get('end_date')

            product = Product.objects.annotate(
                price        = Min('room__price'),
                review_count = Count('review__id'),
                rating       = Avg('review__rating'),
            ).prefetch_related('productimage_set', 'room_set','room_set__reservation_set').get(id = product_id)

            reservations = Reservation.objects.filter(room__product = product)
            rooms        = Room.objects.filter(product = product)
            search_date  = set(pandas.date_range(start_date,end_date)[:-1])

            is_sold_out = True

            for room in rooms:
                for reservation in reservations:
                    reservation_date = set(pandas.date_range(reservation.start_date,reservation.end_date)[:-1])
                    if search_date & reservation_date:
                        room.quantity -= 1 
                if bool(room.quantity) == True:
                    is_sold_out = False
                    break

            result = {
                'product_id'   : product.id,
                'name'         : product.name,
                'grade'        : product.grade if product.grade else 0,
                'address'      : product.address,
                'check_in'     : product.check_in,
                'check_out'    : product.check_out,
                'latitude'     : product.latitude,
                'longtitude'   : product.longtitude,
                'price'        : int(product.price) * len(search_date),
                'rating'       : product.rating if product.rating else 0.0,
                'review_count' : product.review_count if product.review_count else 0,
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
