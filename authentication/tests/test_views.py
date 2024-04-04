from .test_setup import TestSetup
from ..models import User


class TestViews(TestSetup):
    def test_user_cannot_register_with_no_data(self):
        response = self.client.post(self.register_url)
        self.assertEqual(response.status_code, 400)

    def test_user_can_register_corrrectly(self):
        response = self.client.post(self.register_url, self.user_data,formart = "json")
        self.assertEqual(response.status_code, 201)

    def test_user_cannot_login_with_unverified_email(self):
        self.client.post( self.register_url,self.user_data,format="json")
        response = self.client.post(self.login_url,self.user_data, format = "json")
        self.assertEqual(response.status_code, 401)
    def test_user_can_login_after_verification(self):
        self.client.post(self.register_url,self.user_data,format = "json")
        email = self.user_data['email']
        password = self.user_data['password']
        username = self.user_data['username']
        user=User.objects.get(username=username,email=email)
        user.set_password(password)
        user.is_verified = True
        user.save()
        response2 = self.client.post(self.login_url,self.user_data,format = "json")

        self.assertEqual(response2.status_code, 200)
