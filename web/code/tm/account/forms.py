from django import forms
from django.contrib.auth.models import User
from account.models import Profile

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password',
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords do not match.')
        return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name_th', 'last_name_th',
                    'field_of_study', 'college',
                    'graduated_at', 'scholarship',
                    'degree', 'photo',
                    'specialty', 'designated_affiliation',
                    'current_position', 'current_affiliation',
                    'about', 'country',
                    'title', 'scopus_id',
                    'field_of_interest',
                    )
        widgets = {
            'about': forms.Textarea(attrs={'placeholder': 'Enter your short bio here'}),
            'field_of_interest': forms.TextInput(attrs={'placeholder': 'Enter keywords'})
        }
