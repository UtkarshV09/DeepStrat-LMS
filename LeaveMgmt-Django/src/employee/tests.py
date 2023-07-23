from django.test import TestCase
from django.contrib.auth.models import User
from employee.models import Role, Department, Employee

class TestModels(TestCase):

    def setUp(self):
        # Create a User instance
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Create a Role instance
        self.role = Role.objects.create(name='Test Role')

        # Create a Department instance
        self.department = Department.objects.create(name='Test Department')

        # Create an Employee instance
        self.employee = Employee.objects.create(
            user=self.user,
            firstname='Test',
            lastname='User',
            birthday='1990-01-01',
            department=self.department,
            role=self.role,
            startdate='2022-01-01',
            employeetype=Employee.FULL_TIME,
            employeeid='EMP001'
        )

    def test_role_creation(self):
        self.assertEqual(self.role.name, 'Test Role')

    def test_department_creation(self):
        self.assertEqual(self.department.name, 'Test Department')

    def test_employee_creation(self):
        self.assertEqual(self.employee.firstname, 'Test')
        self.assertEqual(self.employee.lastname, 'User')
        self.assertEqual(self.employee.get_full_name, 'Test User')
        self.assertEqual(self.employee.get_age, 33)  # Assuming current year is 2023

    def test_employee_save_method(self):
        # Assuming the 'code_format' function adds 'TEST-' prefix to the id
        self.assertEqual(self.employee.employeeid, 'TEST-EMP001')
