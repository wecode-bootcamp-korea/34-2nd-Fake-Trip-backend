import pandas

from django.views import View
from django.http  import JsonResponse
from datetime     import datetime, timedelta

from products.models       import Room
from core.token_validators import token_validator

class ReservationView(View):
    @token_validator
    def get(self, request):
        try:
            room_id    = request.GET.get('room_id')
            room       = Room.objects.select_related('room').get(id = room_id)
            user       = request.user
            start_date = request.GET.get('start_date',datetime.now().strftime("%Y-%m-%d"))
            end_date   = request.GET.get('end_date')

            if not end_date:
                join_date = datetime.now() + timedelta(days=1)
                end_date  = join_date.strftime("%Y-%m-%d")

            search_date = pandas.date_range(start_date,end_date)[:-1]

            result = {
                'product' : {
                    'id'   : room.product.id,
                    'name' : room.product.name
                },
                'room' : 
                    {   'id'    : room.id,
                        'name'  : room.name,
                        'price' : int(room.price) * len(search_date),
                        'image' : room.image_set.filter(is_main = True).first().url
                    },
                'start_date' : start_date,
                'end_date'   : end_date,
                'user' :
                    {
                        'name'         : user.name,
                        'email'        : user.email,
                        'phone_number' : user.phone_number,
                        'credit'       : user.credit
                    }
            }

            return JsonResponse(result, status = 200)

        except Room.DoesNotExist:
            return JsonResponse({'message' : 'Invalid Room'}, status = 400)