from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from employee.models import Employee
from .forms import UserAddForm, UserLogin
from .views import register_user_view, login_view
from django.contrib.auth.models import AnonymousUser


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
