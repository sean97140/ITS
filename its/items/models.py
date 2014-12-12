import datetime
from django.db import models
from django.utils import timezone
from its.users.models import User

class Action(models.Model):
    action_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
	
    class Meta:
        db_table = "action"
		
    def __str__(self):
        return self.name
	
	
class Status(models.Model):
    status_id = models.AutoField(primary_key=True)
    item = models.ForeignKey('Item')
    action_taken = models.ForeignKey(Action)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.TextField()
	
    class Meta:
        db_table = "status"
		
    def __str__(self):
        return self.status_id

		
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
    possible_owner = models.ForeignKey(User, related_name='item_possible_owner')
    possible_owner_contacted = models.BooleanField(default=False)
    returned_to = models.ForeignKey(User, related_name='item_returned_to')
	
    class Meta:
        db_table = "item"
		
    def __str__(self):
        return self.description
	

	

	


