
from django.db import models
from django import forms
from django.conf import settings
from django.forms import ModelForm
from its.users.models import User
from its.items.models import Item, Location, Category, Status, Action
from django.core.mail import send_mail
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage

def create_user(new_first_name, new_last_name, new_email):

    #import pdb; pdb.set_trace()
            
    new_username = '_' + new_first_name + new_last_name
    i = 0
            
    while User.objects.filter(username=new_username + str(i)).exists():
        i += 1
                
    new_username = new_username + str(i)                 
    new_user = User(first_name = new_first_name, last_name = new_last_name, 
    email = new_email, username = new_username, is_active=False, is_staff=False)
                
    new_user.save()
    
    return new_user

class AdminActionForm(forms.Form):
    
    action_choice = forms.ModelChoiceField(queryset=Action.objects.all(), required=True)
    note = forms.CharField(widget=forms.Textarea, required=False)
            

    def clean(self):
        # require note field on action of OTHER
        cleaned_data = super().clean()
        action_choice = cleaned_data.get("action_choice")
        note = cleaned_data.get("note")
        
        #import pdb; pdb.set_trace()
        
        if str(action_choice) == 'Other' and note == '':
            self.add_error("note", "Note required when choosing action of type Other.")
        
        return cleaned_data
  
   
    def save(self, *args, item_pk, current_user, **kwargs):

        # save status
        item = Item.objects.get(pk=item_pk)
        new_action = Action.objects.get(name=self.cleaned_data['action_choice'])
        new_status = Status(item=item, action_taken=new_action, note=self.cleaned_data['note'], performed_by=current_user).save()
        
    
    
class ItemReturnForm(forms.Form):
    
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.CharField(required=True)
    
    def checkout_email(self, item):
    
        subject = 'Valuable item checked out'
        to = settings.CHECKOUT_EMAIL_TO
        from_email = settings.CHECKOUT_EMAIL_FROM

        ctx = {
            'found_on': str(item.found_on()),
            'possible_owner_name': str(item.possible_owner),
            'returned_by': str(item.last_status().performed_by),
            'returned_to': str(item.returned_to),
            'found_in': item.location.name,
            'category': item.category.name,
            'description': item.description           
        }
        
        message = render_to_string('items/checkout_email.txt', ctx)

        EmailMessage(subject, message, to=to, from_email=from_email).send()
	

    def save(self, *args, item_pk, performed_by, **kwargs):
        
        user_first_name = self.cleaned_data['first_name']
        user_last_name = self.cleaned_data['last_name']
        user_email = self.cleaned_data['email']
        
        if User.objects.filter(first_name=user_first_name, last_name=user_last_name, email=user_email).exists() is True:
            returned_user = User.objects.get(first_name=user_first_name, last_name=user_last_name, email=user_email)
                
        else:
            returned_user = create_user(user_first_name, user_last_name, user_email)
        
        
        returned_item = Item.objects.get(pk=item_pk)
        returned_item.returned_to = returned_user
        returned_item.save()
        
        new_action = Action.objects.get(name="Returned")
        new_status = Status(item=returned_item, action_taken=new_action, performed_by=performed_by, note="Returned to owner").save()
        
        if(returned_item.is_valuable == True):
            self.checkout_email(returned_item)
        
        return returned_item    

class ItemSelectForm(forms.Form):

    item_num = forms.IntegerField(required=True)
    action = forms.CharField(max_length=50, required=True)

    
class AdminItemFilterForm(forms.Form):
    sort_choices= (
        ('pk', 'Date found'),
        ('location', 'Location'),
        ('category', 'Category'),
        ('description', 'Description'),
        ('possible_owner', 'Possible owner'),
    )

    select_location = forms.ModelChoiceField(queryset=Location.objects.all(), required=False)
    select_category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    sort_by = forms.ChoiceField(choices=sort_choices, required=False)
    display_is_valuable_only = forms.BooleanField(required=False)
    display_inactive_only = forms.BooleanField(required=False)
    search_keyword_or_name = forms.CharField(max_length=50, required=False)
    
class ItemFilterForm(forms.Form):

    sort_choices= (
        ('pk', 'Date found'),
        ('location', 'Location'),
        ('category', 'Category'),
        ('description', 'Description'),
        ('possible_owner', 'Possible owner'),
    )

    select_location = forms.ModelChoiceField(queryset=Location.objects.all(), required=False)
    select_category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    sort_by = forms.ChoiceField(choices=sort_choices, required=False)
    display_is_valuable_only = forms.BooleanField(required=False)
    search_keyword_or_name = forms.CharField(max_length=50, required=False)
    

class CheckInForm(ModelForm):
    
    possible_owner_found = forms.BooleanField(required=False)
    username = forms.CharField(required=False, help_text="Or enter a first/last name")
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.CharField(required=False)
    ldap_search = forms.CharField(required=False)
	
    def checkin_email(self, item):
        """
        Send an email to all the admins when a valuable item is checked in
        """
        subject = 'Valuable item checked in'
        to = settings.CHECKIN_EMAIL_TO
        from_email = settings.CHECKIN_EMAIL_FROM

        ctx = {
            'found_on': str(item.found_on()),
            'possible_owner_name': str(item.possible_owner),
            'found_by': str(item.found_by()),
            'found_in': item.location.name,
            'category': item.category.name,
            'description': item.description           
        }
        

        message = render_to_string('items/checkin_email.txt', ctx)

        EmailMessage(subject, message, to=to, from_email=from_email).send()
	
    def user_checkin_email(self, item, possible_owner):
        
        subject = 'An item belonging to you was found'
        to = [possible_owner.email]
        from_email = settings.CHECKIN_EMAIL_FROM

        ctx = {
            'possible_owner_name': str(item.possible_owner),
            'found_in': item.location.name,           
        }
        
        message = render_to_string('items/user_checkin_email.txt', ctx)

        EmailMessage(subject, message, to=to, from_email=from_email).send()
	
    
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
            
        if possible_owner_found and not first_name:
            self.add_error("first_name", "First name required")
            
        if possible_owner_found and not last_name:
            self.add_error("last_name", "Last name required")
            
        if possible_owner_found and not email:
            self.add_error("email", "Email required")

        return cleaned_data
        
    def save(self, *args, current_user, **kwargs):
        
        #import pdb; pdb.set_trace()
        
        user_first_name = self.cleaned_data['first_name']
        user_last_name = self.cleaned_data['last_name']
        user_email = self.cleaned_data['email']
        
        
        if self.cleaned_data.get("possible_owner_found") is True:
        
            if User.objects.filter(first_name=user_first_name, last_name=user_last_name, email=user_email).exists() is True:
                checkin_user = User.objects.get(first_name=user_first_name, last_name=user_last_name, email=user_email)
                
            else:
                checkin_user = create_user(user_first_name, user_last_name, user_email)
            
            self.instance.possible_owner = checkin_user
            
        item = super(CheckInForm, self).save(*args, **kwargs)
        
        new_action = Action.objects.get(name="Checked in")
        new_status = Status(item=item, action_taken=new_action, note="Initial check-in", performed_by=current_user).save()
        
        if(self.cleaned_data['email'] != ''):
            self.user_checkin_email(item, checkin_user)
        
        if(self.cleaned_data['is_valuable'] == True):
            self.checkin_email(item)
            
        return item
            
    class Meta:
        model = Item
        fields = ['location', 'category', 'description', 'is_valuable', 
        'possible_owner_contacted']
