from django.test import TestCase, Client

from products.models import Category, Region, Product, Room, ProductImage

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