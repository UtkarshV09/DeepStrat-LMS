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
