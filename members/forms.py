from django import forms
from .models import Profile, NextOfKin, Beneficiary


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('date_of_birth', 'national_id', 'declaration_confirmed', 'signature', 'profile_photo')
        widgets = {
            'declaration_confirmed': forms.CheckboxInput(),
            'signature': forms.TextInput(attrs={'placeholder': 'Type your full name as signature'})
        }

    def clean_profile_photo(self):
        photo = self.cleaned_data.get('profile_photo')
        if not photo:
            return photo
        content_type = getattr(photo, 'content_type', '')
        if not content_type.startswith('image/'):
            raise forms.ValidationError('Invalid file type. Only images are allowed.')
        max_size = 100 * 1024 * 1024  # 100 MB
        if photo.size > max_size:
            raise forms.ValidationError('Image too large (max 100MB).')
        return photo


class NextOfKinForm(forms.ModelForm):
    class Meta:
        model = NextOfKin
        fields = ('full_name', 'phone_number', 'id_number', 'address', 'relationship')


class BeneficiaryForm(forms.ModelForm):
    class Meta:
        model = Beneficiary
        fields = ('name', 'date_of_birth', 'relationship')


class LeaderMemberForm(forms.Form):
    full_name = forms.CharField(max_length=255)
    phone_number = forms.CharField(max_length=32)
    role = forms.ChoiceField(choices=(('Chairman','Chairman'),('Secretary','Secretary'),('Treasurer','Treasurer'),('Member','Member')))
    status = forms.ChoiceField(choices=(('Visitor','Visitor'),('Active','Active')))
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        # Allow keeping the same phone number when editing by checking initial
        initial_phone = self.initial.get('phone_number') if hasattr(self, 'initial') else None
        if initial_phone and phone == initial_phone:
            return phone
        if User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError('A user with this phone number already exists')
        return phone


class UploadMembersForm(forms.Form):
    file = forms.FileField(help_text='Upload a CSV or XLSX file. Columns: Full Name, Phone, National ID, Role, Status, Email')
