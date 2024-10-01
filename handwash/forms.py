from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, Product, Cart, Supplier  

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description','category', 'price', 'image','ml', 'quantity', 'reorderlevel']
        widgets={
            "name":forms.TextInput(attrs={"class":"form-control"}),
            "price":forms.NumberInput(attrs={"class":"form-control"}),
            "category":forms.Select(attrs={"class":"form-control"}),
            "quantity":forms.NumberInput(attrs={"class":"form-control"}),
            "ml":forms.NumberInput(attrs={"class":"form-control"}),
            "reorderlevel":forms.NumberInput(attrs={"class":"form-control"}),
            "description":forms.Textarea(attrs={"class":"form-control","rows":"4","wrap":"hard"}),
            "image":forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username','email', 'password', 'confirm_password']
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class UserProfileForm(forms.ModelForm):
   
    class Meta:
        model = UserProfile
        fields = [  'age','profile_picture']
   
   

class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['user', 'product', 'quantity']

    

class SupplierLoginForm(AuthenticationForm):
    class Meta:
        model = Supplier
        fields = ['username', 'password']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']


#forms for visualization
from django import forms
from .models import FurnitureRecommendation

class RecommendationForm(forms.ModelForm):
    class Meta:
        model = FurnitureRecommendation
        fields = ['material', 'furniture_type', 'room_type', 'color', 'budget']
