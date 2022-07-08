import jwt

import json

from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile

from products.models import Category, Region, Product, Room, ProductImage
from users.models import User, Review
from faketrip.settings import SECRET_KEY, ALGORITHM

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

class ReviewsTest(TestCase):
    def setUp(self):
        user = User.objects.create(
            id       = 1,
            kakao_pk = 151512,
            email    = 'qwer123@nate.com',
            name     = '위코드'
        )

        Region.objects.create(
            id = 1,
            name = '서울'
        )

        Category.objects.create(
            id = 1,
            name = '호텔'
        )

        Product.objects.create(
            id = 1,
            name = '호텔1',
            grade = 5,
            check_in = '14:00',
            check_out = '11:00',
            address = '호텔1 주소',
            latitude = 33.2406823000,
            longtitude = 126.5317835000,
            region_id = 1,
            category_id = 1)

    def tearDown(self):
        User.objects.all().delete()
        Region.objects.all().delete()
        Category.objects.all().delete()
        Product.objects.all().delete()
        Review.objects.all().delete()

    def test_success_review_post(self):
        client    = Client()
        token     = jwt.encode({'user_id' : 1}, SECRET_KEY, ALGORITHM)
        headers   = {"HTTP_Authorization" : token}
        image     = SimpleUploadedFile('test_image.jpg', b'asda', content_type='image/jpeg')
        body      = {'content' : '멋있어요', 'rating' : '3', 'image' : image}
        response  = client.post('/products/1/review', body, **headers)
       
        self.assertEqual(response.json(),
            {'message' : 'Create Review'}
        )
        self.assertEqual(response.status_code, 201)
    
    def test_fail_review_post_there_is_no_content(self):
        client    = Client()
        token     = jwt.encode({'user_id' : 1}, SECRET_KEY, ALGORITHM)
        headers   = {"HTTP_Authorization" : token}
        image     = SimpleUploadedFile('test_image.jpg', b'asda', content_type='image/jpeg')
        body      = {'rating' : '3', 'image' : image}
        response  = client.post('/products/1/review', body, **headers)
       
        self.assertEqual(response.json(),
            {'message' : 'Insert Content'}
        )
        self.assertEqual(response.status_code, 400)
    
    def test_fail_review_post_there_is_no_rating(self):
        client    = Client()
        token     = jwt.encode({'user_id' : 1}, SECRET_KEY, ALGORITHM)
        headers   = {"HTTP_Authorization" : token}
        image     = SimpleUploadedFile('test_image.jpg', b'asda', content_type='image/jpeg')
        body      = {'content' : 'agag', 'image' : image}
        response  = client.post('/products/1/review', body, **headers)
       
        self.assertEqual(response.json(),
            {'message' : 'Choice Rating'}
        )
        self.assertEqual(response.status_code, 400)
    
    def test_fail_review_post_there_in_no_token(self):
        client    = Client()
        image     = SimpleUploadedFile('test_image.jpg', b'asda', content_type='image/jpeg')
        body      = {'content' : 'agag', 'image' : image}
        response  = client.post('/products/1/review', body)
       
        self.assertEqual(response.json(),
            {'message' : 'Invalid Token'}
        )
        self.assertEqual(response.status_code, 401)
    
    def test_fail_review_post_invalid_token(self):
        client    = Client()
        token     = jwt.encode({'user_id' : 2}, SECRET_KEY, ALGORITHM)
        headers   = {"HTTP_Authorization" : token}
        image     = SimpleUploadedFile('test_image.jpg', b'asda', content_type='image/jpeg')
        body      = {'content' : 'agag', 'image' : image}
        response  = client.post('/products/1/review', body, **headers)
       
        self.assertEqual(response.json(),
            {'message' : 'Invalid User'}
        )
        self.assertEqual(response.status_code, 401)