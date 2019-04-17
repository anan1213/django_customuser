"""

from django import forms
from .models import Url, Category

class UrlCreateForm(forms.ModelForm):

    class Meta:
        model = Url
        fields = '__all__'

class CategoryCreateForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = '__all__'
"""
