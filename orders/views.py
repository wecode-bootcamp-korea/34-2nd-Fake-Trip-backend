import json
import pandas

from enum import Enum

from django.views           import View
from django.http            import JsonResponse
from datetime               import datetime, timedelta
from django.core.exceptions import ValidationError

from products.models       import Room
from core.token_validators import token_validator
from orders.models         import Reservation, ReservationStatus
from core.validators       import Validators

class ReservationStatus(Enum):
    DONE = 1
    CANCEL = 2


class ReservationView(View):
    @token_validator
    def get(self, request):
        try:
            room_id    = request.GET.get('room_id')
            room       = Room.objects.get(id = room_id)
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
                        'image' : room.roomimage_set.filter(is_main = True).first().url
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

    @token_validator
    def post(self, request):
        try:
            data               = json.loads(request.body)
            room_id            = data.get('room_id')
            start_date         = data.get('start_date')
            end_date           = data.get('end_date')
            guest_information  = data.get('guest_information')
            guest_phone_number = guest_information.get('phone_number')
            guest_name         = guest_information.get('name')
            guest_email        = guest_information.get('email')

            CONFIG = {
                'names'         : [guest_name],
                'emails'        : [guest_email],
                'phone_numbers' : [guest_phone_number],
                'dates'         : [start_date, end_date]
            }

            Validators(CONFIG)

            price  = Room.objects.get(id = room_id).price
            credit = request.user.credit

            if price > credit:
                return JsonResponse({'message' : 'Insufficient Balance'}, status = 400)

            Reservation.objects.create(
                room_id               = room_id,
                user                  = request.user,
                start_date            = start_date,
                end_date              = end_date,
                guest_information     = guest_information,
                reservation_status_id = ReservationStatus.DONE.value
            )
            
            request.user.credit -= price
            request.user.save()

            return JsonResponse({'message' : 'Create'}, status = 201)
        
        except ValidationError as e:
            return JsonResponse({'message' : e.message}, status = 400)
