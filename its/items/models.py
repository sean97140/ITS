import datetime
from django.db import models
from django import forms
from django.utils import timezone
from django.forms import ModelForm
from its.users.models import User


class Action(models.Model):
    action_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    machine_name = models.CharField(max_length=50, unique=True)
    weight = models.IntegerField(default=0)
	
    class Meta:
        db_table = "action"
        ordering = ['-weight']
		
    def __str__(self):
        return self.name

        
# should add a performed by field
class Status(models.Model):
    status_id = models.AutoField(primary_key=True)
    item = models.ForeignKey('Item')
    action_taken = models.ForeignKey(Action)
    performed_by = models.ForeignKey(User, null=True, default=None)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.TextField()
	
    class Meta:
        db_table = "status"
        ordering = ['-pk']

    def __str__(self):
        return str(self.status_id)

		
class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
	
    class Meta:
        db_table = "location"
		
    def __str__(self):
        return self.name

		
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
	
    class Meta:
        db_table = "category"
	
    def __str__(self):
        return self.name

		
class Item(models.Model):
    item_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(Location)
    category = models.ForeignKey(Category)
    description = models.TextField()
    is_valuable = models.BooleanField(default=False)
    possible_owner = models.ForeignKey(User, related_name='item_possible_owner', null=True)
    possible_owner_contacted = models.BooleanField(default=False)
    returned_to = models.ForeignKey(User, related_name='item_returned_to', null=True)
    
    
    class Meta:
        db_table = "item"
		
    def __str__(self):
        #import pdb; pdb.set_trace()
        return self.description
		
    # This returns the last updated status, which is the first status
    # it is currently first in the db.
    def last_status(self):
        return Status.objects.filter(item=self).first()
    
    def found_on(self):
        return Status.objects.filter(item=self).last().timestamp
        
    def found_by(self):
        return Status.objects.filter(item=self).last().performed_by
        
	


