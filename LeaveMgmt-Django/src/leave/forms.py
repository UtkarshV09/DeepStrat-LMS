from django import forms
from .models import Leave
import datetime


# Define a form for Leave creation
class LeaveCreationForm(forms.ModelForm):
    # Override the 'reason' field to use a textarea and not be required.
    reason = forms.CharField(
        required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40})
    )

    # Meta class for additional form options
    class Meta:
        # The model that this form is tied to
        model = Leave
        # Fields to exclude from the form, since they will be filled automatically or later in the process.
        exclude = [
            'user',
            'defaultdays',
            'hrcomments',
            'status',
            'is_approved',
            'updated',
            'created',
        ]

    # Clean (validate) the 'enddate' field
    def clean_enddate(self) -> any:
        # Grab the 'enddate' and 'startdate' fields from the cleaned data
        enddate = self.cleaned_data['enddate']
        startdate = self.cleaned_data['startdate']
        today_date = datetime.date.today()

        # Raise an error if either date is in the past.
        if (startdate or enddate) < today_date:  # both dates must not be in the past
            raise forms.ValidationError(
                'Selected dates are incorrect,please select again'
            )
        # Raise an error if the start date is after the end date.
        elif startdate >= enddate:  # TRUE -> FUTURE DATE > PAST DATE,FALSE other wise
            raise forms.ValidationError('Selected dates are wrong')
        # If everything checks out, return the end date as it is.
        return enddate
