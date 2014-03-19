from django import forms

class NewUserForm(forms.Form):
  username = forms.CharField()
  password = forms.CharField(widget=forms.PasswordInput)
  password2 = forms.CharField(label="Re-enter password", widget=forms.PasswordInput)
  
  first_name = forms.CharField()
  last_name = forms.CharField()
  birthdate = forms.DateField()
  
  GROUP_CHOICES = (
    ('patient', 'Patient'),
    ('caretaker', 'Caretaker'),
    ('admin', 'Administrator')
  )
  group = forms.ChoiceField(choices=GROUP_CHOICES)
  