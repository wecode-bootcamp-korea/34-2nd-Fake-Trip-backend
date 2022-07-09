import jwt

from unittest.mock import patch, MagicMock
from django.test   import TestCase, Client

from .models           import User
from faketrip.settings import SECRET_KEY, ALGORITHM

class SinginTest(TestCase):
    def setUp(self):
        User.objects.create(
            id           = 1,
            kakao_pk     = 151512,
            email        = 'qwer123@nate.com',
            name         = '위코드',
            phone_number = None
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
        self.assertEqual(user.phone_number, None)

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