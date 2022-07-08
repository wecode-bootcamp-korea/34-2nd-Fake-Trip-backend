from django.http      import JsonResponse
from django.views     import View
from django.db.models import Q
from django.db.models import Min, Max, IntegerField

from products.models import Product
from orders.models import Reservation

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

