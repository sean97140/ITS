import datetime
from django.db import models
from django import forms
from django.utils import timezone
from django.forms import ModelForm
from its.users.models import User

class LastStatus(models.Model):
    # Because this is only a view in the database we want to 
    # do nothing when the parent object is deleted.
    item = models.ForeignKey("items.Item", on_delete=models.DO_NOTHING)
    status = models.ForeignKey("items.Status", on_delete=models.DO_NOTHING)
    machine_name = models.CharField(max_length=50)

    class Meta:
        db_table = "last_status"
        managed = False

class Action(models.Model):
    action_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    machine_name = models.CharField(max_length=50, unique=True)
    weight = models.IntegerField(default=0)
	
    CHECKED_IN = "CHECKED_IN"
    RETURNED = "RETURNED"
    
    class Meta:
        db_table = "action"
        ordering = ['-weight']
		
    def __str__(self):
        return self.name

        
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
        ordering = ['name']
		
    def __str__(self):
        return self.name

		
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
	
    class Meta:
        db_table = "category"
        ordering = ['name']
	
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
    is_archived = models.BooleanField(default=False)
    
    
    class Meta:
        db_table = "item"
		
    def __str__(self):
        return self.description
		
    # This returns the last updated status, which is the first status
    # it is currently first in the db.
    def last_status(self):
        return Status.objects.filter(item=self).first()
    
    def found_on(self):
        return Status.objects.filter(item=self).last().timestamp
        
    def found_by(self):
        return Status.objects.filter(item=self).last().performed_by
        
	


