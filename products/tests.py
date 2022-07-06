from http        import client
from django.test import TestCase, Client

from products.models import Category, Region, Product, Room, ProductImage
from users.models    import User, Review
from orders.models   import Reservation, ReservationStatus

class ProductListTest(TestCase):
    def setUp(self):
        Category.objects.create(
            id = 1,
            name = '호텔'
        )
        Region.objects.create(
            id = 1,
            name = '제주도'
        )
        Product.objects.bulk_create([
            Product(id = 1,
            name = '호텔1',
            grade = 5,
            check_in = '14:00',
            check_out = '11:00',
            address = '호텔1 주소',
            latitude = 33.2406823000,
            longtitude = 126.5317835000,
            region_id = 1,
            category_id = 1),
            Product(id = 2,
            name = '호텔2',
            grade = 5,
            check_in = '12:00',
            check_out = '11:00',
            address = '호텔2 주소',
            latitude = 33.2406820000,
            longtitude = 126.5317805000,
            region_id = 1,
            category_id = 1),
        ])
        Room.objects.bulk_create([
            Room(name='호텔1방1', product_id='1', price='150000', size='15'),
            Room(name='호텔1방2', product_id='1', price='180000', size='18'),
            Room(name='호텔1방3', product_id='1', price='210000', size='28'),
            Room(name='호텔1방4', product_id='1', price='300000', size='30'),
            Room(name='호텔2방1', product_id='2', price='80000', size='11'),
            Room(name='호텔2방2', product_id='2', price='180000', size='21'),
            Room(name='호텔2방3', product_id='2', price='200000', size='22'),
            Room(name='호텔2방4', product_id='2', price='250000', size='26')
        ])
        ProductImage.objects.bulk_create([
            ProductImage(id = 1, url = 'https://www.naver.com/', is_main = 1, product_id = 1),
            ProductImage(id = 2, url = 'https://www.daum.net/', is_main = 1, product_id = 2)
        ])

    
    def tearDown(self):
        Category.objects.all().delete
        Region.objects.all().delete
        Product.objects.all().delete
    
    def test_product_list_post(self):
        client = Client()
        response = client.get('/products')
        self.assertEqual(response.json(),
        {
            "results": [
                {
                    "id": 1,
                    "name": "호텔1",
                    "grade": 5,
                    "address": "호텔1 주소",
                    "region": "제주도",
                    "check_in": "14:00",
                    "check_out": "11:00",
                    "category": "호텔",
                    "main_image": "https://www.naver.com/",
                    "price": {
                        "min_price": "150000.00",
                        "max_price": "300000.00",
                        "low_price": 150000,
                        "high_price": 300000
                    }
                },
                {
                    "id": 2,
                    "name": "호텔2",
                    "grade": 5,
                    "address": "호텔2 주소",
                    "region": "제주도",
                    "check_in": "12:00",
                    "check_out": "11:00",
                    "category": "호텔",
                    "main_image": "https://www.daum.net/",
                    "price": {
                        "min_price": "80000.00",
                        "max_price": "250000.00",
                        "low_price": 80000,
                        "high_price": 250000
                    }
                }]
        })                
        self.assertEqual(response.status_code, 200)

    def test_product_check_in_ascending_post(self):
        client = Client()
        response = client.get('/products?sort=check_in-ascending')
        self.assertEqual(response.json(),
        {
            "results": [
                {
                    "id": 2,
                    "name": "호텔2",
                    "grade": 5,
                    "address": "호텔2 주소",
                    "region": "제주도",
                    "check_in": "12:00",
                    "check_out": "11:00",
                    "category": "호텔",
                    "main_image": "https://www.daum.net/",
                    "price": {
                        "min_price": "80000.00",
                        "max_price": "250000.00",
                        "low_price": 80000,
                        "high_price": 250000
                    }
                },
                {
                    "id": 1,
                    "name": "호텔1",
                    "grade": 5,
                    "address": "호텔1 주소",
                    "region": "제주도",
                    "check_in": "14:00",
                    "check_out": "11:00",
                    "category": "호텔",
                    "main_image": "https://www.naver.com/",
                    "price": {
                        "min_price": "150000.00",
                        "max_price": "300000.00",
                        "low_price": 150000,
                        "high_price": 300000
                    }
                }
                ]
        })                
        self.assertEqual(response.status_code, 200)

class ProductTest(TestCase):
    def setUp(self):
        user =User.objects.create(
            name = '위코드',
            email = 'alsdgkja@natemar.com',
            kakao_pk = 12397511,
        )

        ReservationStatus.objects.create(id = 1, status = '123')

        product = Product.objects.create(
            id=1,
            name       = '신라호텔',
            address    = '서울특별시 강남구',
            check_in   = '15:00',
            check_out  = '11:00',
            latitude   = 123.1419517111,
            longtitude = 60.1231419112,
        )
        ProductImage.objects.create(
            url = 'aaaaaa.png',
            is_main = True,
            product=product
        )
        Room.objects.create(
            id =1,
            name     = '가나다',
            price    = 100000.00,
            product  = product,
            quantity = 2,
            size     = 20,
        )

        Room.objects.create(
            id=2,
            name     = '가나',
            price    = 120000.00,
            product  = product,
            quantity = 2,
            size     = 20,
        )

        Room.objects.create(
            id=3,
            name     = '가',
            price    = 140000.00,
            product  = product,
            quantity = 2,
            size     = 20,
        )

        Reservation.objects.create(
            user = user,
            room_id = 1,
            start_date = '2022-03-31',
            end_date = '2022-04-02',
            guest_information = {'agag' : 'agagag'},
            reservation_status_id = 1,
        )
        
        Review.objects.create(
            user      = user,
            product   = product,
            content   = '',
            image_url = 'asd',
            rating    = 3,
            room_id   = 1
        )
    
    def tearDown(self):
        ReservationStatus.objects.all().delete()
        Reservation.objects.all().delete()
        Room.objects.all().delete()
        Product.objects.all().delete()
        User.objects.all().delete()
        Review.objects.all().delete()
    
    def test_success_product_get(self):
        client =Client()
        response = client.get('/products/1?start_date=2022-03-31&end_date=2022-04-02')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
            'product_id'   : 1,
            'name'         : '신라호텔',
            'grade'        : 0,
            'address'      : '서울특별시 강남구',
            'check_in'     : '15:00',
            'check_out'    : '11:00',
            'latitude'     : '123.1419517111',
            'longtitude'   : '60.1231419112',
            'price'        : 200000,
            'rating'       : 3.0,
            'review_count' : 1,
            'images'       : [
                {
                    'url'     : 'aaaaaa.png',
                    'is_main' : True
                }
            ],
            'is_sold_out' : False
            }
        )
    
    def test_fail_product_get(self):
        client =Client()
        response = client.get('/products/2?start_date=2022-03-31&end_date=2022-04-02')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'Invalid Product'})