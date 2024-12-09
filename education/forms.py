from django import forms
from .models import PatientEducationResource
from .models import Category

class PatientEducationResourceForm(forms.ModelForm):
    class Meta:
        model = PatientEducationResource
        fields = ['title', 'category', 'content', 'image']
        widgets = {
            'content': forms.HiddenInput(),
        }
        
class ResourceSearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, label="Search Resources")


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']