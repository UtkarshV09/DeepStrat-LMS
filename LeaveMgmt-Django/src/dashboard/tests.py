from django.test import Client, TestCase
from django.contrib.auth.models import User
from employee.models import Employee
from leave.models import Leave
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile


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

    def test_employee_edit_data_view(self):
        user = User.objects.create_user(
            'john', 'john@example.com', 'johnpassword', is_staff=True, is_superuser=True
        )
        self.client.login(username='john', password='johnpassword')
        employee = Employee.objects.create(user=user, firstname='John', lastname='Doe')
        response = self.client.get(reverse('dashboard:edit', args=[employee.id]))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_employee_info_view(self):
        user = User.objects.create_user('john', 'john@example.com', 'johnpassword')
        self.client.login(username='john', password='johnpassword')
        employee = Employee.objects.create(user=user, firstname='John', lastname='Doe')
        response = self.client.get(
            reverse('dashboard:employeeinfo', args=[employee.id])
        )
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

    def test_leaves_view(self):
        user = User.objects.create_user('john', 'john@example.com', 'johnpassword')
        self.client.login(username='john', password='johnpassword')
        leave = Leave.objects.create(user=user, status='pending')
        response = self.client.get(reverse('dashboard:userleaveview', args=[leave.id]))
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

    def test_leave_creation_with_invalid_date(self):
        self.client.login(username='username', password='password')
        response = self.client.post(
            reverse('dashboard:createleave'),
            data={'startdate': '2023-08-01', 'enddate': '2023-07-31'},
        )
        self.assertContains(
            response, 'failed to Request a Leave,please check entry dates'
        )

    def test_leave_creation_with_valid_date(self):
        self.client.login(username='username', password='password')
        response = self.client.post(
            reverse('dashboard:createleave'),
            data={'startdate': '2023-07-25', 'enddate': '2023-07-30'},
        )
        self.assertContains(response, 'Leave Request Sent,wait for Admins response')

    def test_unauthorized_user_access_leaves_list(self):
        self.client.login(username='username', password='password')
        response = self.client.get(reverse('dashboard:leaveslist'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_authorized_user_access_leaves_list(self):
        self.client.login(username='staffusername', password='password')
        response = self.client.get(reverse('dashboard:leaveslist'))
        self.assertEqual(response.status_code, 200)

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

    def test_non_superuser_approve_leave(self):
        self.client.login(username='username', password='password')
        response = self.client.get(reverse('dashboard:approveleave', kwargs={'id': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_superuser_approve_nonexistent_leave(self):
        self.client.login(username='superusername', password='password')
        response = self.client.get(
            reverse('dashboard:approveleave', kwargs={'id': 9999})
        )
        self.assertEqual(response.status_code, 404)

    def test_superuser_approve_valid_leave(self):
        self.client.login(username='superusername', password='password')
        response = self.client.get(reverse('dashboard:approveleave', kwargs={'id': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertContains(response, 'Leave successfully approved for')

    def test_unauthenticated_user_access_cancel_leaves_list(self):
        response = self.client.get(reverse('dashboard:canceleaveslist'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_non_superuser_unapprove_leave(self):
        self.client.login(username='username', password='password')
        response = self.client.get(
            reverse('dashboard:unapproveleave', kwargs={'id': 1})
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_superuser_unapprove_nonexistent_leave(self):
        self.client.login(username='superusername', password='password')
        response = self.client.get(
            reverse('dashboard:unapproveleave', kwargs={'id': 9999})
        )
        self.assertEqual(response.status_code, 404)

    def test_superuser_unapprove_valid_leave(self):
        self.client.login(username='superusername', password='password')
        response = self.client.get(
            reverse('dashboard:unapproveleave', kwargs={'id': 1})
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard:leaveslist'))

    def test_non_superuser_cancel_leave(self):
        self.client.login(username='username', password='password')
        response = self.client.get(reverse('dashboard:cancelleave', kwargs={'id': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_superuser_cancel_nonexistent_leave(self):
        self.client.login(username='superusername', password='password')
        response = self.client.get(
            reverse('dashboard:cancelleave', kwargs={'id': 9999})
        )
        self.assertEqual(response.status_code, 404)

    def test_superuser_cancel_valid_leave(self):
        self.client.login(username='superusername', password='password')
        response = self.client.get(reverse('dashboard:cancelleave', kwargs={'id': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertContains(response, 'Leave is canceled')

    def test_unauthenticated_user_access_leave_rejected_list(self):
        response = self.client.get(reverse('dashboard:leavesrejected'))
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_user_unreject_leave(self):
        response = self.client.get(reverse('dashboard:unrejectleave', kwargs={'id': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_superuser_unreject_valid_leave(self):
        self.client.login(username='superusername', password='password')
        response = self.client.get(reverse('dashboard:unrejectleave', kwargs={'id': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertContains(response, 'Leave is now Unrejected')
