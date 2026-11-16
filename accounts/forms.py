from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class PlatformsField(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple

    def __init__(self, **kwargs):
        super().__init__(choices=User.PLATFORM_CHOICES, **kwargs)


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Juan'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Dela Cruz'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'example@mail.com'}))
    contact_number = forms.CharField(
        max_length=13, required=False,
        validators=[User.phone_validator],
        widget=forms.TextInput(attrs={'placeholder': '09171234567'}),
    )
    platforms = PlatformsField(
        required=True,
        label='Platforms you ride for',
        error_messages={'required': 'Pick at least one platform you ride for.'},
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'contact_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Short hints keep the two-column layout tidy; full rules still show as errors.
        self.fields['username'].help_text = ''
        self.fields['username'].widget.attrs['placeholder'] = 'juanrider'
        self.fields['password1'].help_text = 'At least 8 characters, not all numbers.'
        self.fields['password2'].help_text = ''
        self.fields['password1'].widget.attrs['placeholder'] = '••••••••'
        self.fields['password2'].widget.attrs['placeholder'] = '••••••••'

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_username(self):
        username = super().clean_username()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.RIDER  # Public sign-up is for riders only.
        user.platforms = ','.join(self.cleaned_data['platforms'])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username or email',
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'juanrider or example@mail.com'}),
    )
    password = forms.CharField(
        label='Password', strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••', 'autocomplete': 'current-password'}),
    )

    error_messages = {
        'invalid_login': 'Invalid username/email or password. Please try again.',
        'inactive': 'This account has been deactivated.',
    }


class ProfileForm(forms.ModelForm):
    platforms = PlatformsField(required=False, label='Platforms you ride for')

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email', 'contact_number',
            'profile_photo', 'vehicle_type', 'plate_number',
        )
        widgets = {'profile_photo': forms.ClearableFileInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        if self.instance.is_rider:
            self.initial['platforms'] = self.instance.platform_list
        else:
            # Admins don't ride; hide rider-only fields.
            for name in ('platforms', 'vehicle_type', 'plate_number'):
                self.fields.pop(name)

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        taken = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if taken.exists():
            raise forms.ValidationError('Another account already uses this email.')
        return email

    def clean_profile_photo(self):
        photo = self.cleaned_data.get('profile_photo')
        if photo and hasattr(photo, 'size') and photo.size > 2 * 1024 * 1024:
            raise forms.ValidationError('Profile photo must be 2 MB or smaller.')
        return photo

    def save(self, commit=True):
        user = super().save(commit=False)
        if 'platforms' in self.fields:
            user.platforms = ','.join(self.cleaned_data['platforms'])
        if commit:
            user.save()
        return user
