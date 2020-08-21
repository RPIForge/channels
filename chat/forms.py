from django import forms



class InfoForm(forms.Form):
    request_options =(("3dprinting","3d printing Help"),("lazercutter","Lazer Cutter Help"), ("generalhelp","General Help"))
    
    name = forms.CharField(label='Your name')
    email = forms.EmailField()
    request = forms.MultipleChoiceField(choices = request_options) 
    
    
    def __init__(self, *args, **kwargs):
        super(InfoForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['email'].required = True
        self.fields['request'].required = False
        
        for f in self.fields.values():
            f.widget.attrs = {"placeholder":f.label}
            f.label = ""
            
        