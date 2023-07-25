from django.db import models
from .manager import LeaveManager
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime


# Create your models here.
SICK = 'sick'
CASUAL = 'casual'
EMERGENCY = 'emergency'
STUDY = 'study'
MATERNITY = 'maternity'

# Create a tuple of tuples to store leave types and their human readable names
LEAVE_TYPE = (
    (SICK, 'Sick Leave'),
    (CASUAL, 'Casual Leave'),
    (EMERGENCY, 'Emergency Leave'),
    (STUDY, 'Study Leave'),
    (MATERNITY, 'Maternity Leave'),
)
# Define the default leave days
DAYS = 30


# Create a Leave model
class Leave(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    startdate = models.DateField(
        verbose_name=_('Start Date'),
        help_text='leave start date is on ..',
        null=True,
        blank=False,
    )
    enddate = models.DateField(
        verbose_name=_('End Date'),
        help_text='coming back on ...',
        null=True,
        blank=False,
    )
    leavetype = models.CharField(
        choices=LEAVE_TYPE, max_length=25, default=SICK, null=True, blank=False
    )
    reason = models.CharField(
        verbose_name=_('Reason for Leave'),
        max_length=255,
        help_text='add additional information for leave',
        null=True,
        blank=True,
    )
    defaultdays = models.PositiveIntegerField(
        verbose_name=_('Leave days per year counter'),
        default=DAYS,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=12, default='pending'
    )  # pending,approved,rejected,cancelled
    is_approved = models.BooleanField(default=False)  # hide

    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    # Set the custom manager for the model
    objects = LeaveManager()

    # Meta class for the Leave model
    class Meta:
        verbose_name = _('Leave')
        verbose_name_plural = _('Leaves')
        ordering = ['-created']  # recent objects

    # __str__ method to represent the Leave object as a string
    def __str__(self) -> str:
        return '{0} - {1}'.format(self.leavetype, self.user)

    @property
    def can_apply_leave(self) -> bool:
        num_leaves = Leave.objects.filter(employee=self).count()
        return num_leaves < 7

    @property
    def pretty_leave(self) -> str:
        """
        This provides a pretty representation of the leave object.
        """
        leave = self.leavetype
        user = self.user
        employee = user.employee_set.first().get_full_name
        return '{0} - {1}'.format(employee, leave)

    @property
    def leave_days(self) -> int:
        """
        This property calculates the number of leave days based on start and end dates.
        """
        days_count = ''
        startdate = self.startdate
        enddate = self.enddate
        if startdate > enddate:
            return
        dates = enddate - startdate
        return dates.days

    @property
    def leave_approved(self) -> bool:
        return self.is_approved == True

    # These properties handle the approval, disapproval, cancellation, and rejection of leaves
    @property
    def approve_leave(self) -> any:
        if not self.is_approved:
            self.is_approved = True
            self.status = 'approved'
            self.save()

    @property
    def unapprove_leave(self) -> any:
        if self.is_approved:
            self.is_approved = False
            self.status = 'pending'
            self.save()

    @property
    def leaves_cancel(self) -> any:
        if self.is_approved or not self.is_approved:
            self.is_approved = False
            self.status = 'cancelled'
            self.save()

    @property
    def reject_leave(self) -> any:
        if self.is_approved or not self.is_approved:
            self.is_approved = False
            self.status = 'rejected'
            self.save()

    @property
    def is_rejected(self) -> any:
        return self.status == 'rejected'
