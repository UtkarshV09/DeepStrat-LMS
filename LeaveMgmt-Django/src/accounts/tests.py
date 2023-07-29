from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from employee.models import Employee
from accounts.forms import UserAddForm, UserLogin
from unittest.mock import patch, Mock, MagicMock
from django.test import TestCase
from django.http import HttpRequest
import auth_helper


# testing the UserAddForm
class TestUserAddForm(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test')
        self.change_password_url = reverse('accounts:changepassword')

    def test_change_password_view_authenticated(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.change_password_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/change_password_form.html')

    def test_change_password_view_unauthenticated(self):
        response = self.client.get(self.change_password_url)
        self.assertEqual(response.status_code, 302)  # Should redirect to login page

    def test_change_password_valid_data(self):
        self.client.login(username='test', password='test')
        response = self.client.post(
            self.change_password_url,
            data={
                'old_password': 'test',
                'new_password1': 'newtestpassword',
                'new_password2': 'newtestpassword',
            },
        )
        self.assertEqual(
            response.status_code, 302
        )  # Should redirect after changing password

        # Check if the password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newtestpassword'))

    def test_change_password_invalid_data(self):
        self.client.login(username='test', password='test')
        response = self.client.post(self.change_password_url, data={})
        self.assertEqual(response.status_code, 200)  # Should stay on the same page

        # Check if the password was not changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('test'))

    def tearDown(self):
        self.user.delete()

    def test_form_validity(self):
        form = UserAddForm(
            data={
                'username': 'test',
                'email': 'test@test.com',
                'password1': 'test_password',
                'password2': 'test_password',
            }
        )
        self.assertTrue(form.is_valid())

    def test_form_invalidity(self):
        form = UserAddForm(data={})
        self.assertFalse(form.is_valid())


# Testing the creation of a superuser
class TestSuperUserCreation(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='admin', password='admin'
        )

    def test_superuser_creation(self):
        self.assertEqual(self.superuser.username, 'admin')
        self.assertTrue(self.superuser.is_superuser)

    def tearDown(self):
        self.superuser.delete()


# Testing the registration with an already registered username
class TestUserRegistration(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test')
        self.register_url = reverse('accounts:register')

    def test_register_existing_username(self):
        response = self.client.post(
            self.register_url,
            data={
                'username': 'test',
                'password1': 'test_password',
                'password2': 'test_password',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('A user with that username already exists.' in response.content)

    def tearDown(self):
        self.user.delete()


# Test the login view with a valid user
class TestLoginViewValidUser(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test')
        self.login_url = reverse('accounts:login')

    def test_login_view_valid_user(self):
        response = self.client.post(
            self.login_url, data={'username': 'test', 'password': 'test'}
        )
        self.assertEqual(response.status_code, 302)  # Should redirect to the home page
        self.user = User.objects.get(username='test')
        self.assertTrue(self.user.is_authenticated)

    def tearDown(self):
        self.user.delete()


# Testing the login attempt with wrong password
class TestLoginViewInvalidPassword(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test')
        self.login_url = reverse('accounts:login')

    def test_login_view_invalid_password(self):
        response = self.client.post(
            self.login_url, data={'username': 'test', 'password': 'wrong_password'}
        )
        self.assertEqual(response.status_code, 200)  # Should stay on the same page
        self.assertTrue(
            'Please enter a correct username and password.' in response.content
        )

    def tearDown(self):
        self.user.delete()


# Testing the case where the user tries to change password with invalid old password
class TestChangePasswordInvalidOld(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test')
        self.change_password_url = reverse('accounts:changepassword')

    def test_change_password_invalid_old(self):
        self.client.login(username='test', password='test')
        response = self.client.post(
            self.change_password_url,
            data={
                'old_password': 'wrong_old_password',
                'new_password1': 'new_password',
                'new_password2': 'new_password',
            },
        )
        self.assertEqual(response.status_code, 200)  # Should stay on the same page
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('test'))

    def tearDown(self):
        self.user.delete()


# testing the logout_view
class TestLogoutView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test')
        self.logout_url = reverse('accounts:logout')

    def test_logout_view_authenticated(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)  # Should redirect after logout

        # Check if the user is authenticated
        self.user = User.objects.get(username='test')
        self.assertFalse(self.user.is_authenticated)

    def test_logout_view_unauthenticated(self):
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)  # Should redirect to login page

    def tearDown(self):
        self.user.delete()


# testing the register_user_view with invalid data
class TestRegisterUserViewInvalidData(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register')

    def test_register_view_invalid_data(self):
        response = self.client.post(self.register_url, data={})
        self.assertEqual(response.status_code, 200)  # Should stay on the same page

        # Check if the user was not created
        users = User.objects.all()
        self.assertEqual(len(users), 0)


# testing the login_view with invalid data
class TestLoginViewInvalidData(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('accounts:login')

    def test_login_view_invalid_data(self):
        response = self.client.post(self.login_url, data={})
        self.assertEqual(response.status_code, 200)  # Should stay on the same page


# testing the UserLogin form
class TestUserLogin(TestCase):
    def test_form_validity(self):
        form = UserLogin(data={'username': 'test', 'password': 'test_password'})
        self.assertTrue(form.is_valid())

    def test_form_invalidity(self):
        form = UserLogin(data={})
        self.assertFalse(form.is_valid())


# testing the register_user_view
class TestRegisterUserView(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register')

    def test_register_view(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')


# testing the login_view
class TestLoginView(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('accounts:login')

    def test_login_view(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')


# Add more tests for your views, forms, models as needed.


class UserViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test')
        self.employee = Employee.objects.create(user=self.user, is_blocked=False)
        self.users_list_url = reverse('accounts:users')
        self.users_unblock_url = reverse(
            'accounts:userunblock', kwargs={'id': self.user.id}
        )
        self.users_block_url = reverse(
            'accounts:userblock', kwargs={'id': self.user.id}
        )
        self.users_blocked_list_url = reverse('accounts:erasedusers')

    def test_user_list_view(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.users_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/users_table.html')

    def test_user_unblock_view(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.users_unblock_url)
        self.assertEqual(response.status_code, 302)  # Should redirect after unblocking

        # Check if the user is unblocked
        self.employee.refresh_from_db()
        self.assertFalse(self.employee.is_blocked)

    def test_user_block_view(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.users_block_url)
        self.assertEqual(response.status_code, 302)  # Should redirect after blocking

        # Check if the user is blocked
        self.employee.refresh_from_db()
        self.assertTrue(self.employee.is_blocked)

    def test_user_blocked_list_view(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.users_blocked_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/all_deleted_users.html')

    def tearDown(self):
        self.user.delete()


"""
SSO TESTING
"""


class TestAuthHelper(TestCase):
    @patch('msal.ConfidentialClientApplication')
    def test_get_msal_app(self, mock_msal_app):
        mock_cache = MagicMock()
        auth_helper.get_msal_app(mock_cache)
        mock_msal_app.assert_called()

    @patch('auth_helper.get_msal_app')
    @patch('msal.ConfidentialClientApplication.initiate_auth_code_flow')
    def test_get_sign_in_flow(self, mock_auth_flow, mock_msal_app):
        mock_msal_app.return_value = mock_auth_flow
        auth_helper.get_sign_in_flow()
        mock_auth_flow.assert_called()

    @patch('auth_helper.get_msal_app')
    @patch('auth_helper.load_cache')
    @patch('auth_helper.save_cache')
    @patch('msal.ConfidentialClientApplication.acquire_token_by_auth_code_flow')
    def test_get_token_from_code(
        self, mock_token, mock_save_cache, mock_load_cache, mock_msal_app
    ):
        mock_request = Mock(spec=HttpRequest)
        mock_msal_app.return_value = mock_token
        auth_helper.get_token_from_code(mock_request)
        mock_token.assert_called()

    def test_store_user(self):
        mock_request = Mock(spec=HttpRequest)
        mock_user = {
            'displayName': 'Mocked User',
            'mail': 'test@mail.com',
            'mailboxSettings': {'timeZone': 'UTC'},
        }
        auth_helper.store_user(mock_request, mock_user)
        self.assertEqual(
            mock_request.user,
            {
                'is_authenticated': True,
                'name': 'Mocked User',
                'email': 'test@mail.com',
                'timeZone': 'UTC',
            },
        )

    @patch('auth_helper.get_msal_app')
    @patch('auth_helper.load_cache')
    @patch('auth_helper.save_cache')
    @patch('msal.ConfidentialClientApplication.acquire_token_silent')
    def test_get_token(
        self, mock_token, mock_save_cache, mock_load_cache, mock_msal_app
    ):
        mock_request = Mock(spec=HttpRequest)
        mock_msal_app.return_value = mock_token
        mock_token.return_value = {'access_token': 'mocked_access_token'}
        result = auth_helper.get_token(mock_request)
        mock_token.assert_called()
        self.assertEqual(result, 'mocked_access_token')

    def test_remove_user_and_token(self):
        mock_request = Mock(spec=HttpRequest)
        mock_request.session = {'token_cache': 'token', 'user': 'user'}
        auth_helper.remove_user_and_token(mock_request)
        self.assertFalse('token_cache' in mock_request.session)
        self.assertFalse('user' in mock_request.session)
