import jwt

from unittest.mock                  import patch, MagicMock
from django.test                    import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile

from .models           import User, Review
from faketrip.settings import SECRET_KEY, ALGORITHM
from products.models   import Region, Category, Product

class SinginTest(TestCase):
    def setUp(self):
        User.objects.create(
            id       = 1,
            kakao_pk = 151512,
            email    = 'qwer123@nate.com',
            name     = '위코드'
        )

    def tearDown(self):
        User.objects.all().delete()

    @patch("core.social_apis.requests")
    def test_success_kakao_signin(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    'id': 151512, 
                    'connected_at': '2022-07-06T16:22:22Z', 
                    'properties': {
                        'nickname': '위코드', 
                        'profile_image': 'http://가짜.이미지.jpg', 
                        'thumbnail_image': 'http://가짜.이미지2.jpg'
                        }, 
                    'kakao_account': {
                        'profile_nickname_needs_agreement': False, 
                        'profile_image_needs_agreement': False, 
                        'profile': {
                            'nickname': '위코드', 
                            'thumbnail_image_url': 'http://가짜.이미지2.jpg', 
                            'profile_image_url': 'http://가짜.이미지.jpg', 
                            'is_default_image': False}, 
                            'has_email': True, 
                            'email_needs_agreement': False, 
                            'is_email_valid': True, 
                            'is_email_verified': True, 
                            'email': 'qwer123@nate.com'}}

            status_code = 200
    
        mocked_requests.get = MagicMock(return_value = MockedResponse())
        headers             = {'HTTP_token' : '가짜 access_token'}
        response            = client.get('/users/signin', **headers)
        user                = User.objects.get(id = 1)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Authorization'),
            jwt.encode({'user_id' : user.id}, SECRET_KEY, ALGORITHM)
        )
        self.assertEqual(response.json()['message'], 'SUCCESS')
        
    @patch('core.social_apis.requests')
    def test_success_changed_kakao_information_user_signin(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    'id': 151512, 
                    'connected_at': '2022-07-06T16:22:22Z', 
                    'properties': {
                        'nickname': '코드', 
                        'profile_image': 'http://가짜.이미지.jpg', 
                        'thumbnail_image': 'http://가짜.이미지2.jpg'
                        }, 
                    'kakao_account': {
                        'profile_nickname_needs_agreement': False, 
                        'profile_image_needs_agreement': False, 
                        'profile': {
                            'nickname': '위코드', 
                            'thumbnail_image_url': 'http://가짜.이미지2.jpg', 
                            'profile_image_url': 'http://가짜.이미지.jpg', 
                            'is_default_image': False}, 
                            'has_email': True, 
                            'email_needs_agreement': False, 
                            'is_email_valid': True, 
                            'is_email_verified': True, 
                            'email': 'qwer@nate.com'}}
    
            status_code = 200
        
        mocked_requests.get = MagicMock(return_value = MockedResponse())
        headers             = {'HTTP_token' : '가짜 access_token'}
        response            = client.get('/users/signin', **headers)
        user                = User.objects.get(id = 1)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Authorization'),
            jwt.encode({'user_id' : user.id}, SECRET_KEY, ALGORITHM)
        )
        self.assertEqual(response.json()['message'], 'SUCCESS')
        self.assertEqual(user.name, '코드')
        self.assertEqual(user.email, 'qwer@nate.com')

    @patch("core.social_apis.requests")
    def test_fail_kakao_signin(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {'msg': 'this access token does not exist', 'code': -401}
                
            status_code = 401
    
        mocked_requests.get = MagicMock(return_value = MockedResponse())
        headers             = {'HTTP_token' : '가짜 access_token'}
        response            = client.get('/users/signin', **headers)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.headers.get('Authorization'),None)
        self.assertEqual(response.json()['message'], 'Invalid Token')

class ReviewTest(TestCase):
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
        body      = {'content' : '멋있어요', 'rating' : '3', 'image' : image, 'product_id' : 1}
        response  = client.post('/users/review', body, **headers)
       
        self.assertEqual(response.json(),
            {'message' : 'Create Review'}
        )
        self.assertEqual(response.status_code, 201)
    
    def test_fail_review_post_there_is_no_content(self):
        client    = Client()
        token     = jwt.encode({'user_id' : 1}, SECRET_KEY, ALGORITHM)
        headers   = {"HTTP_Authorization" : token}
        image     = SimpleUploadedFile('test_image.jpg', b'asda', content_type='image/jpeg')
        body      = {'rating' : '3', 'image' : image, 'product_id' : 1}
        response  = client.post('/users/review', body, **headers)
       
        self.assertEqual(response.json(),
            {'message' : 'Insert Content'}
        )
        self.assertEqual(response.status_code, 400)
    
    def test_fail_review_post_there_is_no_rating(self):
        client    = Client()
        token     = jwt.encode({'user_id' : 1}, SECRET_KEY, ALGORITHM)
        headers   = {"HTTP_Authorization" : token}
        image     = SimpleUploadedFile('test_image.jpg', b'asda', content_type='image/jpeg')
        body      = {'content' : 'agag', 'image' : image, 'product_id' : 1}
        response  = client.post('/users/review', body, **headers)
       
        self.assertEqual(response.json(),
            {'message' : 'Choice Rating'}
        )
        self.assertEqual(response.status_code, 400)
    
    def test_fail_review_post_there_in_no_token(self):
        client    = Client()
        image     = SimpleUploadedFile('test_image.jpg', b'asda', content_type='image/jpeg')
        body      = {'content' : 'agag', 'image' : image, 'product_id' : 1}
        response  = client.post('/users/review', body)
       
        self.assertEqual(response.json(),
            {'message' : 'Invalid Token'}
        )
        self.assertEqual(response.status_code, 401)
    
    def test_fail_review_post_invalid_token(self):
        client    = Client()
        token     = jwt.encode({'user_id' : 2}, SECRET_KEY, ALGORITHM)
        headers   = {"HTTP_Authorization" : token}
        image     = SimpleUploadedFile('test_image.jpg', b'asda', content_type='image/jpeg')
        body      = {'content' : 'agag', 'image' : image, 'product_id' : 1}
        response  = client.post('/users/review', body, **headers)
       
        self.assertEqual(response.json(),
            {'message' : 'Invalid User'}
        )
        self.assertEqual(response.status_code, 401)