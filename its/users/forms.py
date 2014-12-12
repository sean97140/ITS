from django import forms
from .models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
        )

    def save(self, *args, **kwargs):
        self.instance.set_password(self.cleaned_data.pop("password"))
        return super(UserForm, self).save(*args, **kwargs)
