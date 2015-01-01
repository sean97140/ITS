from django.db import models
from django import forms
from django.forms import ModelForm
from its.users.models import User
from its.items.models import Item, Location, Category, Status, Action


class CheckInForm(ModelForm):
    
    #possible_owner = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    possible_owner_found = forms.BooleanField(required=False)
    username = forms.CharField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.CharField(required=False)
    ldap_search = forms.CharField(required=False)
	
	# use LDAP to look up ODIN username
	# If Possible owner is defined, then create a user.
	# Override clean method to check if possible owner is used
	# to make sure the optional form is set to required. 
	# need to import superclass
	# Also use add error to throw a validation erro exception
	
    def clean(self):
        #import pdb; pdb.set_trace()
        cleaned_data = super(CheckInForm, self).clean()
        username = cleaned_data.get("username")
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        email = cleaned_data.get("email")
        possible_owner_found = cleaned_data.get("possible_owner_found")
		
        if possible_owner_found and not username:
            self.add_error("username", "username required")
            #raise forms.ValidationError("Username required")
            
        if possible_owner_found and not first_name:
            self.add_error("first_name", "First name required")
            
        if possible_owner_found and not last_name:
            self.add_error("last_name", "Last name required")
            
        if possible_owner_found and not email:
            self.add_error("email", "Email required")

        return cleaned_data
        
    def save(self, *args, found_by, **kwargs):
    
        if(self.cleaned_data['username'] != ''):
            new_username = self.cleaned_data['username']
            new_first_name = self.cleaned_data['first_name']
            new_last_name = self.cleaned_data['last_name']
            new_email = self.cleaned_data['email']
                
            new_user = User(first_name = new_first_name, last_name = new_last_name,
                            email = new_email, username = new_username,
                            is_active=False, is_staff=False)
                            
            new_user.save()
            
        else:
            new_user = None
                        
        self.instance.found_by = found_by
        self.instance.possible_owner = new_user
        item = super(CheckInForm, self).save(*args, **kwargs)
        
        new_action = Action.objects.get(name="Checked in")
        new_status = Status(item=item, action_taken=new_action, note="Initial check-in").save()

        return item

            
    class Meta:
        model = Item
        fields = ['location', 'category', 'description', 'is_valuable', 
        'possible_owner_contacted']
