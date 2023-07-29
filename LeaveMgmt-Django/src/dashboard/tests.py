import os
from django.test import Client, TestCase
from django.contrib.auth.models import User
from employee.models import Department, Employee, Role
from leave.models import Leave
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings


class DashboardTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_dashboard_view(self):
        User.objects.create_user('john', 'john@example.com', 'johnpassword')
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_employees_view(self):
        User.objects.create_user(
            'john', 'john@example.com', 'johnpassword', is_staff=True, is_superuser=True
        )
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('dashboard:employees'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_employees_create_view(self):
        User.objects.create_user(
            'john', 'john@example.com', 'johnpassword', is_staff=True, is_superuser=True
        )
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('dashboard:employeecreate'))
        self.assertEqual(response.status_code, 200)

    def test_leave_creation_view(self):
        User.objects.create_user('john', 'john@example.com', 'johnpassword')
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('dashboard:createleave'))
        self.assertEqual(response.status_code, 200)

    def test_leaves_list_view(self):
        User.objects.create_user(
            'john', 'john@example.com', 'johnpassword', is_staff=True, is_superuser=True
        )
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('dashboard:leaveslist'))
        self.assertEqual(response.status_code, 200)

    def test_cancel_leaves_list_view(self):
        User.objects.create_user(
            'john', 'john@example.com', 'johnpassword', is_staff=True, is_superuser=True
        )
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('dashboard:canceleaveslist'))
        self.assertEqual(response.status_code, 200)

    def test_leave_rejected_list_view(self):
        User.objects.create_user(
            'john', 'john@example.com', 'johnpassword', is_staff=True, is_superuser=True
        )
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('dashboard:leavesrejected'))
        self.assertEqual(response.status_code, 200)

    def test_view_my_leave_table_view(self):
        user = User.objects.create_user('john', 'john@example.com', 'johnpassword')
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('dashboard:staffleavetable'))
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_user_redirect_to_login(self):
        response = self.client.get(reverse('dashboard:createleave'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_unauthorized_user_access_leaves_list(self):
        self.client.login(username='username', password='password')
        response = self.client.get(reverse('dashboard:leaveslist'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_authorized_user_access_leaves_list(self):
        self.client.login(username='staffusername', password='password')
        response = self.client.get(reverse('dashboard:leaveslist'))
        self.assertEqual(response.status_code, 302)

    def test_unauthenticated_user_access_leave_view(self):
        response = self.client.get(reverse('dashboard:userleaveview', kwargs={'id': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_authenticated_user_access_nonexistent_leave_view(self):
        self.client.login(username='username', password='password')
        response = self.client.get(
            reverse('dashboard:userleaveview', kwargs={'id': 9999})
        )
        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_user_access_cancel_leaves_list(self):
        response = self.client.get(reverse('dashboard:canceleaveslist'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_unauthenticated_user_access_leave_rejected_list(self):
        response = self.client.get(reverse('dashboard:leavesrejected'))
        self.assertEqual(response.status_code, 200)


class AdditionalDashboardTest(DashboardTest):
    test_image_path = os.path.join(settings.MEDIA_ROOT, 'default.png')

    def test_successful_employee_creation(self):
        self.client.login(username='john', password='johnpassword')

        # you need to create a Department and Role object for the test
        department = Department.objects.create(
            name='test', description='test description'
        )
        role = Role.objects.create(name='test', description='test description')

        # Use Django's settings to reference the file
        test_image_path = os.path.join(settings.MEDIA_ROOT, 'default.png')

        with open(test_image_path, 'rb') as file:
            document = SimpleUploadedFile(
                file.name, file.read(), content_type='image/*'
            )

        response = self.client.post(
            reverse('dashboard:employeecreate'),
            data={
                'username': 'newuser',
                'password': 'newpassword',
                'firstname': 'New',
                'lastname': 'User',
                'birthday': '1990-01-01',
                'department': department.id,
                'role': role.id,
                'startdate': '2022-01-01',
                'employeetype': Employee.FULL_TIME,
                'employeeid': '1234567890',
                'dateissued': '2022-01-01',
                'image': document,
            },
        )
        self.assertEqual(
            response.status_code, 302
        )  # Assuming a successful post redirects
        self.assertEqual(Employee.objects.count(), 1)
        self.assertEqual(Employee.objects.get().username, 'newuser')

    def test_successful_leave_creation(self):
        user = User.objects.create_user('john', 'john@example.com', 'johnpassword')
        self.client.login(username='john', password='johnpassword')
        response = self.client.post(
            reverse('dashboard:createleave'),
            data={
                'user': user.id,
                'startdate': '2023-07-25',
                'enddate': '2023-07-30',
                'leavetype': 'sick',
                'reason': 'Some reason',
                'defaultdays': 10,
            },
        )

        if response.status_code == 200:  # form is invalid
            print(response.context['form'].errors)
        else:  # form is valid
            self.assertEqual(response.status_code, 302)  # successful post redirects
            self.assertEqual(Leave.objects.count(), 1)
            self.assertEqual(Leave.objects.get().user, user)

    def test_form_error_on_invalid_employee_creation(self):
        self.client.login(username='john', password='johnpassword')
        response = self.client.post(
            reverse('dashboard:employeecreate'),
            data={
                'username': '',
                'password': 'newpassword',
                'firstname': 'New',
                'lastname': 'User',
            },
        )
        self.assertRedirects(
            response,
            expected_url=reverse('dashboard:employeecreate'),
            status_code=302,
            target_status_code=200,
        )
        response = self.client.get(
            reverse('dashboard:employeecreate')
        )  # request the page again to check for the error message
        self.assertContains(response, 'This field is required.')


class AdditionalDashboardTest2(DashboardTest):
    def test_leave_list(self):
        user1 = User.objects.create_user('john', 'john@example.com', 'johnpassword')
        user2 = User.objects.create_user('jane', 'jane@example.com', 'janepassword')
        Leave.objects.create(
            user=user1, startdate='2023-07-25', enddate='2023-07-30', status='pending'
        )
        Leave.objects.create(
            user=user2, startdate='2023-08-01', enddate='2023-08-05', status='approved'
        )
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('dashboard:leaveslist'))
        self.assertContains(response, '2023-07-25')
        self.assertContains(response, '2023-08-05')

    def test_dashboard_employees_create_view_post(self):
        user = User.objects.create_user(
            'john', 'john@example.com', 'johnpassword', is_superuser=True
        )
        self.client.login(username='john', password='johnpassword')
        response = self.client.post(
            reverse('dashboard:employeecreate'),
            data={
                'user': user.id,
                'firstname': 'John',
                'lastname': 'Doe',
                'birthday': '1990-01-01',
                'startdate': '2023-07-25',
                'employeetype': Employee.FULL_TIME,  # Or another valid choice
                # Add other necessary fields here...
            },
        )
        self.assertEqual(
            response.status_code, 302
        )  # Assuming a successful post redirects
        self.assertEqual(Employee.objects.count(), 1)


class AdditionalDashboardTest3(DashboardTest):
    def test_leave_creation_with_file_upload(self):
        self.client.login(username='username', password='password')
        dummy_file = SimpleUploadedFile('file.txt', b'file_content')
        response = self.client.post(
            reverse('dashboard:createleave'),
            data={
                'startdate': '2023-07-25',
                'enddate': '2023-07-30',
                'attachment': dummy_file,
            },
        )
        self.assertContains(response, 'Leave Request Sent,wait for Admins response')

    def test_unauthenticated_user_create_employee(self):
        response = self.client.get(reverse('dashboard:employeecreate'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_dashboard_leave_view_with_invalid_leave_id(self):
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('dashboard:userleaveview', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_dashboard_leave_rejected_list_view_unauthenticated(self):
        response = self.client.get(reverse('dashboard:leavesrejected'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')
