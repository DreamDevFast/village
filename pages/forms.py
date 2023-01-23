from django import forms
from django.utils.translation import ugettext_lazy as _

from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

from general.models import EmailField
from general.mail import send_mail_to_admin
from general.decorators import reorder_fields


class FeedbackForm(forms.Form):
    feedback = forms.CharField(label=_("Feedback"), widget=forms.Textarea)
    captcha = ReCaptchaField(label='', widget=ReCaptchaWidget())

    def get_sender(self):
        return NotImplementedError  # Implement in subclasses.

    def send(self):
        send_mail_to_admin(
            _("Villages.io Feedback"),
            self.get_sender(), 'feedback_email.txt',
            {'feedback': self.cleaned_data['feedback']})


@reorder_fields()
class AnonymousFeedbackForm(FeedbackForm):
    name = forms.CharField(label=_("Name"), required=False)
    email = forms.EmailField(label=_("Email"), max_length=EmailField.MAX_EMAIL_LENGTH)
    field_order = ['name', 'email', 'feedback', 'captcha']

    def get_sender(self):
        data = self.cleaned_data
        return data.get('name'), data['email']


class UserFeedbackForm(FeedbackForm):
    def __init__(self, profile, *args, **kwargs):
        self.profile = profile
        super(UserFeedbackForm, self).__init__(*args, **kwargs)

    def get_sender(self):
        return self.profile
