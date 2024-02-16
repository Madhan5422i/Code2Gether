from django.forms import ModelForm, ImageField
from .models import Room,Profile
from django.contrib.auth.models import User
from django import forms


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']



from .models import User, Profile, about

class UserForm(forms.ModelForm):
    bio = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username','bio']
        
from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    profile_pic = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'your-css-class'}), required=False)

    class Meta:
        model = Profile
        fields = ['profile_pic']  # add other fields if needed
