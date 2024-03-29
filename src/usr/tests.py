from rest_framework import status

from common.tests import TestCase
from . import factories


class TestUser(TestCase):
    def test_login(self):
        data = {
            'username': self.device.email,
            'password': '123'
        }
        response = self.device_client.post('/login', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('token'))

    def test_registration(self):
        # check if created successfully
        data = factories.RegistrationFactory.build()
        response = self.admin_client.post('/users', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Try to login using newly created user
        login_response = self.device_client.post('/login', data={'username': data['email'],
                                                                 'password': data['password']})
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_registration_duplicate_email(self):
        data = factories.RegistrationFactory.build()
        data['email'] = self.device.email
        response = self.admin_client.post('/users', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_missing_fields(self):
        keys = factories.RegistrationFactory.build().keys()

        # check if created successfully
        for k in keys:
            data = factories.RegistrationFactory.build()
            del data[k]
            response = self.admin_client.post('/users', data=data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_extra_fields(self):
        data = factories.RegistrationFactory.build()
        data['is_superuser'] = True
        response = self.admin_client.post('/users', data=data)

        self.assertEqual(response.data['is_superuser'], False)

    def test_invalid_email(self):
        data = factories.RegistrationFactory.build(email='shit0@example')
        response = self.admin_client.post('/users', data=data)
        self.assertEqual(response.status_code, 400)

    def test_update(self):
        user = factories.UserFactory()
        response = self.admin_client.patch('/users/%s' % user.id, data={'zip_code': '456-789'})
        user.refresh_from_db()
        self.assertEqual(user.zip_code, response.data['zip_code'])

    def test_update_extra_info(self):
        user = factories.UserFactory()
        self.admin_client.patch('/users/%s' % user.id, data={'is_active': False})
        user.refresh_from_db()
        self.assertEqual(user.is_active, True)

        user = factories.UserFactory()
        response = self.admin_client.patch('/users/%s' % user.id, data={'fullname': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_change(self):
        user = factories.UserFactory()
        response = self.admin_client.post('/users/%s/actions/change_password' % user.id,
                                          data={'new_password': '456', 'old_password': '123'})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.admin_client.post('/users/%s/actions/change_password' % user.id,
                                          data={'new_password': '456', 'old_password': '123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_change_blank(self):
        user = factories.UserFactory()
        response = self.admin_client.post('/users/%s/actions/change_password' % user.id,
                                          data={'new_password': '', 'old_password': '123'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_request(self):
        user = factories.UserFactory()
        old_pw_reset_key = user.password_reset_key

        self.admin_client.post('/users/actions/password_reset', data={'email': user.email})
        user.refresh_from_db()
        self.assertNotEqual(old_pw_reset_key, user.password_reset_key)
        self.assertEqual(user.is_password_reset, False)

        # with non-exists email
        resp = self.admin_client.post('/users/actions/password_reset',
                                      data={'email': 'no@mail.com'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_request_ntimes(self):
        user = factories.UserFactory()

        self.admin_client.post('/users/actions/password_reset', data={'email': user.email})
        user.refresh_from_db()
        old_pw_reset_key = user.password_reset_key

        self.admin_client.post('/users/actions/password_reset', data={'email': user.email})
        user.refresh_from_db()

        self.assertEqual(old_pw_reset_key, user.password_reset_key)

    def test_password_reset(self):
        user = factories.UserFactory()
        data = {'email': user.email,
                'reset_key': user.password_reset_key,
                'new_password': '789'}


        # Lets try to reset password using default key of the user
        resp = self.admin_client.put('/users/actions/password_reset', data=data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # request a reset now
        self.admin_client.post('/users/actions/password_reset', data={'email': user.email})
        user.refresh_from_db()

        # reset password
        data['reset_key'] = user.password_reset_key
        self.admin_client.put('/users/actions/password_reset', data=data)

        # try to login with new password
        resp = self.admin_client.post('/login', data={'username': user.email, 'password': '789'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_email_verification(self):
        user = factories.UserFactory()
        self.assertEqual(user.is_email_verified, False)

        # Test with bad key
        resp = self.admin_client.post('/users/actions/verify_email',
                                      data={'key': 'wrong key'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # Test with correct key
        self.admin_client.post('/users/actions/verify_email',
                               data={'key': user.unverified_email_key})
        user.refresh_from_db()
        self.assertEqual(user.is_email_verified, True)

    def test_address_factory(self):
        factories.AddressFactory(user=self.user)
        self.assertEqual(self.user.usr_address_set.count(), 1)

    def test_add_address(self):
        data = factories.AddressBaseFactory()
        resp = self.user_client.post('/users/%s/addresses' % self.user.id, data=data)
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED, resp)

        data = factories.AddressBaseFactory(phone='84984')
        resp = self.user_client.post('/users/%s/addresses' % self.user.id, data=data)
        self.assertEqual(resp.status_code, self.status_code.HTTP_400_BAD_REQUEST, resp)

    def test_create_favorite_product(self):
        from catalog.factories import ProductFactory

        user = factories.UserFactory()
        product = ProductFactory(user=user)

        resp = self.user_client.post('/users/%s/favorite/products' % self.user.id,
                                     data={'id': product.id})
        self.assertEqual(resp.status_code, self.status_code.HTTP_204_NO_CONTENT)

        resp = self.user_client.get('/users/%s/favorite/products' % self.user.id)
        self.assertEqual(resp.meta['count'], 1)

        resp = self.user_client.delete(
            '/users/%s/favorite/products/%s' % (self.user.id, product.id)
        )
        self.assertEqual(resp.status_code, self.status_code.HTTP_204_NO_CONTENT)

    def test_settings(self):
        resp = self.user_client.patch('/users/%s/setting' % self.user.id,
                                      data={'daily_price_till_days': '4'})
        resp = self.user_client.get('/users/%s/setting' % self.user.id)
        self.assertEqual(resp.status_code, self.status_code.HTTP_200_OK)
        self.assertEqual(resp.data['daily_price_till_days'], 4)


class PermissionTest(TestCase):
    def test_user_default_group(self):
        new_user = factories.RegistrationFactory()
        resp = self.device_client.post('/users', data=new_user)

        self.assertIn('User', [d['name'] for d in resp.data.get('groups')])

    def test_user_create_member(self):
        new_user = factories.RegistrationFactory()
        resp = self.user_client.post('/users', data=new_user)
        self.assertEqual(resp.data['user'], self.user.id)
