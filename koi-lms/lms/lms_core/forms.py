from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Student

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class QueryForm(forms.Form):
    query_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Ask your question here...',
            'class': 'form-control'
        }),
        label='Your Question'
    )


class ProfileUpdateForm(forms.ModelForm):
    # User fields
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )

    class Meta:
        model = Student
        fields = [
            'phone', 'date_of_birth', 'program', 'status',
            'gpa', 'address', 'postcode', 'state',
            'international', 'scholarship'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'program': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Program'}),
            'status': forms.Select(attrs={'class': 'form-control'},
                                   choices=[('Active','Active'),('Suspended','Suspended'),('Inactive','Inactive')]),
            'gpa': forms.NumberInput(attrs={'class': 'form-control','step':'0.01','min':'0','max':'4'}),
            'address': forms.Textarea(attrs={'class': 'form-control','rows':3,'placeholder':'Address'}),
            'postcode': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-control'},
                                  choices=[('NSW','NSW'),('VIC','VIC'),('QLD','QLD'),
                                           ('SA','SA'),('WA','WA'),('TAS','TAS'),
                                           ('ACT','ACT'),('NT','NT')]),
            'international': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'scholarship': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }

    def save(self, commit=True):
        # Save Student fields
        student = super(ProfileUpdateForm, self).save(commit=False)
        # Update related User fields
        user = student.user
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            student.save()
        return student
