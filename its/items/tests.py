from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from model_mommy.mommy import make
from its.users.models import User
from its.items.models import Item, Location, Category, Action, Status
from its.items.forms import AdminActionForm, AdminItemFilterForm, ItemFilterForm, ItemArchiveForm, CheckInForm
from its.items.views import admin_itemlist, adminaction, itemlist, checkin, printoff
from unittest.mock import patch, Mock


def create_user():
    user = make(User, is_active=True)
    user.set_password("password")
    user.save()
    return user

def create_full_user(first_name, last_name, email):
    user = make(User, first_name=first_name, last_name=last_name, email=email, is_active=False, is_staff=False)
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
        
        #new_category = make(Category)
        #new_location = make(Location)
        #
        #data = {'location': new_location.pk, 'category': new_category.pk, 
        #'description': "test", 'username': "", 'first_name': "", 
        #'last_name': "", 'email': ""}
        
        with patch("its.items.views.CheckInForm.is_valid", return_value=True):
            with patch("its.items.views.CheckInForm.save", return_value=Mock(pk=123)) as save:
                data = {"foo": "bar"}
                response = self.client.post(reverse("checkin"), data)
                self.assertTrue(save.call_args[1]['current_user'] == user)
                self.assertRedirects(response, reverse("printoff", args=[123]), target_status_code=404)


    def test_invalid_post(self):
        user = create_user()
        self.client.login(username=user.username, password="password")

        with patch("its.items.views.CheckInForm.is_valid", return_value=False):
            data = {"foo": "bar"}
            response = self.client.post(reverse("checkin"), data)
            self.assertEqual(response.status_code, 200)

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
     
    def test_valid_archive_post(self):
        
        user = create_staff()
        self.client.login(username=user.username, password="password")
        
        with patch('its.items.views.ItemArchiveForm.is_valid', return_value=True) as m:
            with patch('its.items.views.ItemArchiveForm.save', return_value=True) as save:
                form = {'test': 'data'}
                
                request = self.client.post(reverse("admin-itemlist"), form)
                self.assertRedirects(request, reverse("admin-itemlist"))
                
    def test_invalid_archive_post(self):
        
        user = create_staff()
        self.client.login(username=user.username, password="password")
        
        with patch('its.items.views.ItemArchiveForm.is_valid', return_value=False) as m:
                form = {'test': 'data'}
                
                request = self.client.post(reverse("admin-itemlist"), form)
                self.assertEqual(200, request.status_code)
                
        #new_item = make(Item)
        #new_status = make(Status, item=new_item)
        #form = {'action': 'Archive selected items', 
        #        'archive-' + str(new_item.pk): 'on'
        #        }
        #request = self.client.post(reverse("admin-itemlist"), data=form)
        #self.assertRedirects(request, reverse("admin-itemlist"))
        
        # new_item was updated, and the reference is now stale, update it.
        #new_item = Item.objects.get(item_id=new_item.pk)
        #self.assertEqual(True, new_item.is_archived)
        
        
        
# Form tests
        
class CheckInFormTest(TestCase):
    def test_clean_errors(self):
        data = {
            "possible_owner_found": "1",
            "first_name": "",
            "last_name": "",
            "email": "",
            "username": "a"
        }
        with patch("its.items.forms.ModelForm.clean", return_value=data) as m:
            with patch("its.items.forms.check_ldap", return_value=False) as ldap: 
                with patch("its.items.forms.CheckInForm.add_error") as add_error:
                    form = CheckInForm()
                    form.clean()
                    add_error.assert_any_call_with("first_name", "First name required")
                    add_error.assert_any_call_with("last_name", "Last name required")
                    add_error.assert_any_call_with("email", "Email required")
                    add_error.assert_any_call_with("username", "Invalid username, enter a valid username or leave blank.")
     
    def test_clean_no_errors(self):
        data = {
            "possible_owner_found": "1",
            "first_name": "Test",
            "last_name": "Test",
            "email": "test@test.com",
            "username": "a"
        }
        with patch('its.items.forms.ModelForm.clean', return_value=data) as m:
            with patch('its.items.forms.check_ldap', return_value=True) as ldap:
                form = CheckInForm()
                cleaned_data = form.clean()
                self.assertTrue(cleaned_data['possible_owner_found'] == '1')
                self.assertTrue(cleaned_data['username'] == 'a')
                self.assertTrue(cleaned_data['first_name'] == 'Test')
                self.assertTrue(cleaned_data['last_name'] == 'Test')
                self.assertTrue(cleaned_data['email'] == 'test@test.com')
    
    def test_save_new_user(self):
        
        fixtures = ["actions.json"]
        
        new_item = make(Item)
        new_action = make(Action, machine_name=Action.CHECKED_IN)
        new_status = make(Status, action_taken=new_action, item=new_item)
        new_category = make(Category)
        new_location = make(Location)
                
        data = {
                'location': new_location,
                'category': new_category,
                'description': new_item.description,
                'is_valuable' : True,
                'username': "",
                'possible_owner_contacted': True,
                'possible_owner_found': True,
                'first_name': "test",
                'last_name': "test",
                'email': "test@test.com",
        }
        
        user = create_user()
        
        with patch('its.items.forms.CheckInForm.clean', return_value=data) as m:
            form = CheckInForm(data)
            form.cleaned_data = data
            
            with patch("its.items.forms.ModelForm.save", return_value=new_item) as save:
                form.save(current_user=user)
        
                new_user = User.objects.get(first_name=data['first_name'], last_name=data['last_name'], email=data['email'])
            
                self.assertTrue(data['first_name'] == new_user.first_name)
                self.assertTrue(data['last_name'] == new_user.last_name)
                self.assertTrue(data['email'] == new_user.email)
 
    def test_save_old_user(self):
        
        fixtures = ["actions.json"]
        
        new_item = make(Item)
        new_action = make(Action, machine_name=Action.CHECKED_IN)
        new_status = make(Status, action_taken=new_action, item=new_item)
        new_category = make(Category)
        new_location = make(Location)
                
        data = {
                'location': new_location,
                'category': new_category,
                'description': new_item.description,
                'is_valuable' : True,
                'username': "",
                'possible_owner_contacted': True,
                'possible_owner_found': True,
                'first_name': "test",
                'last_name': "test",
                'email': "test@test.com",
        }
        
        user = create_user()
        old_patron = create_full_user(data['first_name'], data['last_name'], data['email'])
        
        original_num_users = User.objects.all().count()
        
        with patch('its.items.forms.CheckInForm.clean', return_value=data) as m:
            form = CheckInForm(data)
            form.cleaned_data = data
            with patch("its.items.forms.ModelForm.save", return_value=new_item) as save:
                form.save(current_user=user)
                new_user = User.objects.get(first_name=data['first_name'], last_name=data['last_name'], email=data['email'])
            
                self.assertTrue(original_num_users == User.objects.all().count())


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
