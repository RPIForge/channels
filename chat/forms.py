from django import forms
from . import models


class InfoForm(forms.Form):
    request_options =(
    ("making", "Id like to come in and make something"),
    ("resources", "Id like to come in and use something"),
    ("general question", "I have a general question about the forge"),
    
    #("3d printing", "Id like to come in and Print something"),
    #("laser cutting", "Id like to come in and Cut something"),
    #("electronics", "Id like to come in and Solder something"),
    #("sewing", "Id like to come in and Sew something"),
    #("scanning", "Id like to come in and Scan something"),
    #("file optimization", "Id like to optimize my model/cut plan"),
    #("cad help", "I have a CAD model question or concern"),
    #("charges", "I have a question about pricing"),
    #("covid", "I have a question about your COVID response"),
    #("general question", "I have a general question about the forge"),

    )
    
    name = forms.CharField(label="Your name")
    email = forms.EmailField()
    request = forms.MultipleChoiceField(choices = request_options) 
    
    
    def __init__(self, *args, **kwargs):
        super(InfoForm, self).__init__(*args, **kwargs)
        self.fields["name"].required = True
        self.fields["email"].required = True
        self.fields["request"].required = False
        
        
        self.fields["name"].label = ""
        self.fields["email"].label = ""
        self.fields["request"].label = "" 
        
        self.fields["name"].widget.attrs = {"placeholder":"Name"}
        self.fields["email"].widget.attrs = {"placeholder":"Email"}
        

            

class FileForm(forms.ModelForm):  
    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)
        self.fields["file"].label = ""
        self.fields["file"].widget.attrs = {"placeholder":"Upload File"}
        
    
    class Meta:                                 
        model = models.FileLog 
        fields = ("file",)