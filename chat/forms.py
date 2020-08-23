from django import forms
from . import models


class InfoForm(forms.Form):
    request_options =(("3dprinting","3d printing Help"),("lasercutter","Laser Cutter Help"), ("generalhelp","General Help"))
    
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