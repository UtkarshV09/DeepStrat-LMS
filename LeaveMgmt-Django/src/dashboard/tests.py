from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from employee.models import Employee
from leave.models import Leave
from unittest.mock import patch

class DashboardTestCases(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='john', password='johnpassword')
        self.employee = Employee.objects.create(user=self.user, firstname='John', lastname='Doe')
        self.leave = Leave.objects.create(user=self.user, reason='Vacation')

    def test_dashboard_access_not_authenticated(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/accounts/login')

    def test_dashboard_access_authenticated(self):
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'summary')

    def test_dashboard_employees_not_authenticated(self):
        response = self.client.get(reverse('dashboard_employees'))
        self.assertRedirects(response, '/')

    @patch('employee.models.Employee.objects.all')
    def test_dashboard_employees_authenticated(self, mock_all):
        mock_all.return_value = [self.employee]
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('dashboard_employees'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_employee_info_not_authenticated(self):
        response = self.client.get(reverse('dashboard_employee_info', args=[1]))
        self.assertRedirects(response, '/')

    @patch('django.shortcuts.get_object_or_404')
    def test_dashboard_employee_info_authenticated(self, mock_get):
        mock_get.return_value = self.employee
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('dashboard_employee_info', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')

    def test_leave_creation_not_authenticated(self):
        response = self.client.get(reverse('leave_creation'))
        self.assertRedirects(response, '/accounts/login')

    def test_leave_creation_authenticated(self):
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('leave_creation'))
        self.assertEqual(response.status_code, 200)

    def test_leaves_list_not_authenticated(self):
        response = self.client.get(reverse('leaves_list'))
        self.assertRedirects(response, '/')
        
    # Add more test cases for other views
