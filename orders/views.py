import json
from tracemalloc import start

from django.views import View
from django.http  import JsonResponse
from datetime     import datetime

from products.models       import Room
from core.token_validators import token_validator
from orders.models         import Reservation

class ReservationView(View):
    @token_validator
    def get(self, request, room_id):
        try:
            room       = Room.objects.get(id = room_id)
            user       = request.user
            start_date = request.GET.get('start_date',datetime.now().strftime("%Y-%m-%d"))
            end_date   = request.GET.get('end_date')

            if not end_date:
                join_date = datetime.now()+ timedelta(days=1)
                end_date  = join_date.strftime("%Y-%m-%d")

            result = {
                'room' : 
                    {
                        'name'  : room.name,
                        'price' : room.price,
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

    def post(self, request, room_id):
        try:
            data       = json.loads(request.body)
            room       = Room.objects.get(id = room_id)
            start_date = data.get(start_date)
            end_date   = data.get(end_date)

            guest_information = data.get(guest_information)

            if room.price > request.user.credit:
                return JsonResponse({'message' : 'Money Is Scarce'}, status = 400)

            Reservation.objects.create(
                room               = room,
                reservation_status = None,
                user               =  request.user,
                guest_information  = guest_information,
                start_date         = start_date,
                end_date           = end_date
            )

        except Room.DoesNotExist:
            return JsonResponse({'message' : 'Invalid Room'}, status = 400)
        