import datetime
import unittest
from django.test import TestCase
from employee.models import Role, Department, Employee
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from employee.utility import check_code_length, code_format


class RoleModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Role.objects.create(name='test', description='test description')

    def test_role_creation(self):
        role = Role.objects.get(id=1)
        self.assertEqual(role.name, 'test')
        self.assertEqual(role.description, 'test description')


class DepartmentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Department.objects.create(name='test', description='test description')

    def test_department_creation(self):
        department = Department.objects.get(id=1)
        self.assertEqual(department.name, 'test')
        self.assertEqual(department.description, 'test description')


class EmployeeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create(username='testuser', password='12345')
        test_role = Role.objects.create(name='test', description='test description')
        test_department = Department.objects.create(
            name='test', description='test description'
        )

        test_image_path = 'path_to_your_test_image'  # Please replace it with your actual test image path

        with open(test_image_path, 'rb') as file:
            document = SimpleUploadedFile(
                file.name, file.read(), content_type='image/*'
            )

        Employee.objects.create(
            user=test_user,
            image=document,
            firstname='test first',
            lastname='test last',
            birthday='1990-01-01',
            department=test_department,
            role=test_role,
            startdate='2020-01-01',
            employeetype=Employee.FULL_TIME,
            employeeid='1234567890',
            dateissued='2020-01-01',
        )

    def test_employee_creation(self):
        employee = Employee.objects.get(id=1)
        self.assertEqual(employee.firstname, 'test first')
        self.assertEqual(employee.lastname, 'test last')
        self.assertEqual(employee.employeeid, '1234567890')
        self.assertEqual(employee.user.username, 'testuser')
        self.assertEqual(employee.role.name, 'test')
        self.assertEqual(employee.department.name, 'test')

    def test_get_full_name(self):
        employee = Employee.objects.get(id=1)
        self.assertEqual(employee.get_full_name, 'test first test last')

    def test_get_age(self):
        employee = Employee.objects.get(id=1)
        current_year = datetime.date.today().year
        self.assertEqual(employee.get_age, current_year - 1990)


class TestUtilityFunctions(TestCase):
    def test_check_code_length(self):
        self.assertTrue(check_code_length('ABCDE'))  # test with 5 characters
        self.assertTrue(check_code_length('ABCDEF'))  # test with more than 5 characters
        self.assertFalse(check_code_length('ABCD'))  # test with less than 5 characters
        self.assertFalse(check_code_length(''))  # test with empty string
        self.assertFalse(check_code_length(None))  # test with None

    def test_code_format(self):
        self.assertEqual(
            code_format('A0091'), 'RGL/A0/091'
        )  # test with a valid code without RGL prefix
        self.assertEqual(
            code_format('RGLA0091'), 'RGL/A0/091'
        )  # test with a valid code with RGL prefix
        self.assertEqual(
            code_format('RGL/A0/091'), 'RGL/A0/091'
        )  # test with a valid code with RGL prefix and slashes
        self.assertIsNone(
            code_format('A091')
        )  # test with a code less than 5 characters
        self.assertIsNone(code_format(''))  # test with an empty string
        self.assertIsNone(code_format(None))  # test with None
