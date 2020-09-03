from django import forms
from . import models


class InfoForm(forms.Form):
    request_options =(
    ('3d printing', 'Id like to come in and Print something'),
    ('laser cutting', 'Id like to come in and Cut something'),
    ('electronics', 'Id like to come in and Solder Something'),
    ('sewing', 'Id like to come in and Sew Something'),
    ('scanning', 'Id like to come in and Scan something'),
    ('cad help', 'I have a CAD Model Question or Concern'),
    ('file optimization', 'How can i optimize my model/cut plan?'),
    ('general question', 'I have a general question about the forge'),
    ('hours', 'What are your hours'),
    ('covid', 'How are you responding to COVID'),
    )
    
    name = forms.CharField(label='Your name')
    email = forms.EmailField()
    request = forms.MultipleChoiceField(choices = request_options) 
    
    
    def __init__(self, *args, **kwargs):
        super(InfoForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['email'].required = True
        self.fields['request'].required = False
        
        
        self.fields['name'].label = ""
        self.fields['email'].label = ""
        self.fields['request'].label = "" 
        
        self.fields['name'].widget.attrs = {"placeholder":"Name"}
        self.fields['email'].widget.attrs = {"placeholder":"Email"}
        

            

class FileForm(forms.ModelForm):  
    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)
        self.fields['file'].label = ""
        self.fields['file'].widget.attrs = {"placeholder":"Upload File"}
        
    
    class Meta:                                 
        model = models.FileLog 
        fields = ('file',)