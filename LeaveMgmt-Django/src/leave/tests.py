from django.test import TestCase
from django.contrib.auth.models import User
from leave.models import Leave

class TestLeaveModel(TestCase):

    def setUp(self):
        # Create a User instance
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Create a Leave instance
        self.leave = Leave.objects.create(
            user=self.user,
            startdate='2023-01-01',
            enddate='2023-01-07',
            leavetype=Leave.SICK
        )

    def test_leave_creation(self):
        self.assertEqual(self.leave.user.username, 'testuser')
        self.assertEqual(self.leave.leavetype, 'sick')
        self.assertEqual(self.leave.leave_days, 6)
        self.assertFalse(self.leave.is_approved)

    def test_leave_approval(self):
        self.leave.approve_leave
        self.assertTrue(self.leave.is_approved)
        self.assertEqual(self.leave.status, 'approved')

    def test_leave_unapproval(self):
        self.leave.approve_leave
        self.leave.unapprove_leave
        self.assertFalse(self.leave.is_approved)
        self.assertEqual(self.leave.status, 'pending')

    def test_leave_cancellation(self):
        self.leave.approve_leave
        self.leave.leaves_cancel
        self.assertFalse(self.leave.is_approved)
        self.assertEqual(self.leave.status, 'cancelled')

    def test_leave_rejection(self):
        self.leave.approve_leave
        self.leave.reject_leave
        self.assertFalse(self.leave.is_approved)
        self.assertEqual(self.leave.status, 'rejected')
