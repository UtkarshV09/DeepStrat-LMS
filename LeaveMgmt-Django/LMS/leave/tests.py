from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, timedelta
from leave.models import SICK, Leave
from leave.forms import LeaveCreationForm
import datetime


class LeaveModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.leave = Leave.objects.create(
            user=self.user,
            startdate=date.today(),
            enddate=date.today() + timedelta(days=4),
            leavetype="sick",
            reason="Test reason",
            defaultdays=30,
            status="pending",
        )

    # Test 1: Check if the correct number of leave days is calculated
    def test_leave_days(self):
        self.assertEqual(self.leave.leave_days, 4)

    # Test 2: Check if the leave is approved correctly
    def test_approve_leave(self):
        self.leave.approve_leave
        self.assertEqual(self.leave.is_approved, True)
        self.assertEqual(self.leave.status, "approved")

    # Test 3: Check if the leave is unapproved correctly
    def test_unapprove_leave(self):
        self.leave.approve_leave
        self.leave.unapprove_leave
        self.assertEqual(self.leave.is_approved, False)
        self.assertEqual(self.leave.status, "pending")

    # Test 4: Check if the leave is cancelled correctly
    def test_leave_cancel(self):
        self.leave.leaves_cancel
        self.assertEqual(self.leave.is_approved, False)
        self.assertEqual(self.leave.status, "cancelled")

    # Test 5: Check if the leave is rejected correctly
    def test_reject_leave(self):
        self.leave.reject_leave
        self.assertEqual(self.leave.is_approved, False)
        self.assertEqual(self.leave.status, "rejected")

    # Test 6: Check if an approved leave can be approved again
    def test_approve_approved_leave(self):
        self.leave.approve_leave
        with self.assertRaises(ValueError):
            self.leave.approve_leave

    # Test 7: Check if an unapproved leave can be unapproved again
    def test_unapprove_unapproved_leave(self):
        with self.assertRaises(ValueError):
            self.leave.unapprove_leave

    # Test 8: Check if a cancelled leave can be cancelled again
    def test_cancel_cancelled_leave(self):
        self.leave.leaves_cancel
        with self.assertRaises(ValueError):
            self.leave.leaves_cancel

    # Test 9: Check if a rejected leave can be rejected again
    def test_reject_rejected_leave(self):
        self.leave.reject_leave
        with self.assertRaises(ValueError):
            self.leave.reject_leave

    # Test 10: Check if leave days are calculated correctly when startdate and enddate are the same
    def test_single_day_leave(self):
        self.leave.startdate = date.today()
        self.leave.enddate = date.today()
        self.leave.save()
        self.assertEqual(self.leave.leave_days, 0)


class LeaveCreationFormTest(TestCase):
    def test_form_valid(self):
        form_data = {
            "startdate": datetime.date.today() + datetime.timedelta(days=1),
            "enddate": datetime.date.today() + datetime.timedelta(days=5),
            "leavetype": SICK,  # use the actual value from LEAVE_TYPE
            "reason": "Medical appointment",
        }
        form = LeaveCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_invalid_dates_in_past(self):
        form_data = {
            "startdate": datetime.date.today() - datetime.timedelta(days=5),
            "enddate": datetime.date.today() - datetime.timedelta(days=1),
            "leavetype": "Sick Leave",
            "reason": "Medical appointment",
        }
        form = LeaveCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["enddate"], ["Selected dates are incorrect,please select again"]
        )

    def test_form_invalid_startdate_after_enddate(self):
        form_data = {
            "startdate": datetime.date.today() + datetime.timedelta(days=5),
            "enddate": datetime.date.today() + datetime.timedelta(days=1),
            "leavetype": "Sick Leave",
            "reason": "Medical appointment",
        }
        form = LeaveCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["enddate"], ["Selected dates are wrong"])
