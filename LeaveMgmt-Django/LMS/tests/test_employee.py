import datetime
import unittest
from django.test import TestCase
from employee.models import Role, Department, Employee
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from employee.utility import check_code_length, code_format
from django.conf import settings
import os


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
        # self.assertIsNone(code_format(''))  # test with an empty string
        # self.assertIsNone(code_format(None))  # test with None
