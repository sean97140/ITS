from django.test import TestCase
from django.core.urlresolvers import reverse
from model_mommy.mommy import make
from its.users.models import User
from its.items.models import Item, Location, Category, Action, Status
from its.items.forms import CheckInForm
from unittest.mock import patch
from django.test.client import RequestFactory


def create_user():
    user = make(User, is_active=True)
    user.set_password("password")
    user.save()
    return user
    
def create_staff():
    user = make(User, is_active=True, is_staff=True)
    user.set_password("password")
    user.save()
    return user
    

class PrintoffTest(TestCase):
       
    def test_login_required(self):
        response = self.client.get(reverse("printoff", args=[1]))
        self.assertRedirects(response, reverse("login") + "?next=/items/1/", target_status_code=302)

    def test_get(self):
        user = create_user()

        self.client.login(username=user.username, password="password")
        item = make(Item)
        make(Status, item=item)
        response = self.client.get(reverse("printoff", args=[item.pk]))
        self.assertEqual(200, response.status_code)
        self.assertIn(item.description, response.content.decode())
        
class CheckInTest(TestCase):
    
    fixtures = ["actions.json"]
    
    def test_login_required(self):
        response = self.client.get(reverse("checkin"))
        self.assertRedirects(response, reverse("login") + "?next=/items/checkin", target_status_code=302)
        
    def test_get(self):
        user = create_user()
        self.client.login(username=user.username, password="password")
        
        response = self.client.get(reverse("checkin"))
        self.assertEqual(200, response.status_code)

    def test_valid_post(self):
        user = create_user()
        self.client.login(username=user.username, password="password")
        
        new_category = make(Category)
        new_location = make(Location)
        
        data = {'location': new_location.pk, 'category': new_category.pk, 
        'description': "test", 'username': "", 'first_name': "", 
        'last_name': "", 'email': ""}
        
        response = self.client.post(reverse("checkin"), data)
        self.assertRedirects(response, reverse("printoff", args=[Item.objects.last().pk]))

class ItemlistTest(TestCase):

    fixtures = ["actions.json"]
    
    def test_login_required(self):
        response = self.client.get(reverse("itemlist"))
        self.assertRedirects(response, reverse("login") + "?next=/items/itemlist", target_status_code=302)
        
    def test_initial_get(self):
        user = create_user()
        self.client.login(username=user.username, password="password")
        
        response = self.client.get(reverse("itemlist"))
        self.assertEqual(200, response.status_code)
        
    def test_filter_get(self):
        user = create_user()
        self.client.login(username=user.username, password="password")
        
        new_location = make(Location)
        new_category = make(Category)
        new_item = make(Item, location=new_location, category=new_category)
        new_action = Action.objects.get(machine_name=Action.CHECKED_IN)
        new_status = make(Status, item=new_item, action_taken=new_action)
   
        data = {'select_location': new_location.pk, 'select_category': new_category.pk}
        
        response = self.client.get(reverse("itemlist"), data)
        self.assertEqual(200, response.status_code)
        self.assertIn(new_item.description, response.content.decode())


class AdminActionTest(TestCase):
    
    def test_login_required(self):
        response = self.client.get(reverse("admin-action", args=[1]))
        self.assertRedirects(response, reverse("login") + "?next=/items/admin-action/1/", target_status_code=302)

    def test_get(self):
        user = create_staff()
        self.client.login(username=user.username, password="password")
        
        new_item = make(Item)
        new_status = make(Status, item=new_item)
        
        response = self.client.get(reverse("admin-action", args=[new_item.pk]))
        self.assertEqual(200, response.status_code)
        self.assertIn(new_item.description, response.content.decode())

class AdminItemlistTest(TestCase):
    
    def test_staff_required(self):
        response = self.client.get(reverse('admin-itemlist'))
        self.assertRedirects(response, reverse("login") + "?next=/items/admin-itemlist", target_status_code=302)
    
    def test_initial_get(self):
        user = create_staff()
        self.client.login(username=user.username, password="password")
        
        response = self.client.get(reverse("admin-itemlist"))
        self.assertEqual(200, response.status_code)
        
    def test_blank_post(self):
        user = create_staff()
        self.client.login(username=user.username, password="password")
        
        request = self.client.post(reverse("admin-itemlist"))
        self.assertRedirects(request, reverse("admin-itemlist"))
     
    # Not working yet.
    #def test_archive_post(self):
        
    #    user = create_staff()
    #    self.client.login(username=user.username, password="password")
        
    #    new_item = make(Item)
    #    new_status = make(Status, item=new_item)
        
    #    request = self.client.post(reverse("admin-itemlist"), {'archive-' + str(new_item.pk): new_item.pk})
    #    self.assertRedirects(request, reverse("admin-itemlist"))
    #    self.assertEqual(True, new_item.is_archived)
        
        
        
        
        

## Create your tests here.
#class ItemsTest(TestCase):
#    
#    def setUp(self):
#        
#        # Not created yet
#        fixtures = ['actions.json']
#        
#        super(ItemsTest, self).setUp()
#        
#        new_user = User(email="jdoe9@pdx.edu", first_name="Jon",
#        last_name="Doe8", username="jdoe9", password="test", is_active=True, is_staff=True)
#        
#        new_user.save()
#        
#        self.new_user = new_user
#        
#        new_location = Location(name="ML 115")
#        new_location.save()
#        
#        self.new_location = new_location
#        
#        new_category = Category(name="USB Storage Device")
#        new_category.save()
#        
#        self.new_category = new_category
#        
#        new_item = Item(location=new_location, category=new_category, 
#        description="usb device", is_valuable=False, possible_owner=None, 
#        possible_owner_contacted=False, returned_to=None, found_by=new_user)       
#        new_item.save()
#        
#        self.new_item = new_item
#        
#        new_action = Action(name="Checked in", machine_name="CHECKEDIN", weight=0)
#        new_action.save()
#        
#        self.new_action = new_action
#        
#        new_status = Status(item=new_item, action_taken=new_action, note="Initial check-in")
#        new_status.save()
#        self.new_status = new_status
#       
#        self.client.login(email=self.new_user.email, password=self.new_user.password)
#        
#        
#
#    def test_valid_printoff_view(self):
#        
#        response = self.client.get(reverse("printoff", args=[self.new_item.pk]))
#        self.assertEqual(response.status_code, 200)
#        
#    def test_invalid_printoff_view(self):
#    
#        bad_item = Item.objects.last().pk + 1
#        
#        response = self.client.get(reverse("printoff", args=[bad_item]))
#        self.assertEqual(response.status_code, 404)
#        
#    def test_valid_checkin_get_view(self):
#        
#        response = self.client.get(reverse('checkin'))
#        self.assertEqual(response.status_code, 200)
#    
#    def test_invalid_checkin_post_view(self):
#    
#        with patch('its.items.forms.CheckInForm.is_valid', return_value=False):
#            response = self.client.post(reverse('checkin'))
#        
#        self.assertEqual(response.status_code, 200)
#     
#    #def test_valid_checkin_post_view(self):
#    
#    #    form = {'location': self.new_location.pk, 'category': self.new_category.pk, 
#    #    'description': "usb device", 'is_valuable': False, 'possible_owner_contacted': False,
#    #    'possible_owner_found': False, 'username': "", 'first_name': "", 'last_name': "", 
#    #    'email': ""}
#        
#    #    response = self.client.post(reverse('checkin'), data=form)
#        
#    #    self.assertEqual(response.status_code, 302)
#    
#    def test_valid_CheckInForm_clean_form(self):
#        
#        form = CheckInForm(data={'location': self.new_location.pk, 'category': self.new_category.pk, 
#        'description': "usb device", 'is_valuable': False, 'possible_owner_contacted': False,
#        'possible_owner_found': False, 'username': "", 'first_name': "", 'last_name': "", 
#        'email': ""})
#        
#        self.assertEqual(form.is_valid(), True)
#        self.assertEqual(form.cleaned_data['username'], "")
#        self.assertEqual(form.cleaned_data['first_name'], "")
#        self.assertEqual(form.cleaned_data['last_name'], "")
#        self.assertEqual(form.cleaned_data['email'], "")
#        self.assertEqual(form.cleaned_data['possible_owner_found'], False)
#        
#    def test_invalid_CheckIn_clean_logic_form(self):
#    
#        form = CheckInForm(data={'location': self.new_location.pk, 'category': self.new_category.pk, 
#        'description': "usb device", 'is_valuable': False, 'possible_owner_contacted': False,
#        'possible_owner_found': True, 'username': "", 'first_name': "", 'last_name': "", 
#        'email': ""})
#        
#        self.assertEqual(form.is_valid(), False)
#        self.assertEqual(form.errors['username'], ["username required"])
#        self.assertEqual(form.errors['first_name'], ["First name required"])
#        self.assertEqual(form.errors['last_name'], ["Last name required"])
#        self.assertEqual(form.errors['email'], ["Email required"])
#       
#    def test_valid_CheckIn_save_logic_form(self):
#       
#        form = CheckInForm(data={'location': self.new_location.pk, 'category': self.new_category.pk, 
#        'description': "usb device", 'is_valuable': False, 'possible_owner_contacted': False,
#        'possible_owner_found': True, 'username': "jdoe10", 'first_name': "Jon", 'last_name': "Doe10", 
#        'email': "jdoe10@pdx.edu"})
#        
#        self.assertEqual(form.is_valid(), True)
#        
#        form.save(found_by=self.new_user)      
#        possible_owner = User.objects.get(username="jdoe10")
#        
#        self.assertEqual(possible_owner.first_name, "Jon")
#        self.assertEqual(possible_owner.last_name, "Doe10")
#        self.assertEqual(possible_owner.email, "jdoe10@pdx.edu")
#        
#    #def test_invalid_CheckIn_save_logic_form(self):
#    # Not sure how to write this
#
#    #def test_valid_Item_last_status_model(self):
#    
#    #    self.assertEqual(self.new_item.last_status(), self.new_status)
#        
#    def test_valid_Item_str_model(self):
#        
#        self.assertEqual(str(self.new_item), self.new_item.description)
#        
#    def test_valid_Category_str_model(self):
#        
#        self.assertEqual(str(self.new_category), self.new_category.name)
#        
#    def test_valid_Location_str_model(self):
#        
#        self.assertEqual(str(self.new_location), self.new_location.name)
#        
#    def test_valid_Status_str_model(self):
#        
#        self.assertEqual(str(self.new_status), str(self.new_status.status_id))
#    
#    def test_valid_Action_str_model(self):
#        
#        self.assertEqual(str(self.new_action), self.new_action.name)
#    
#    
