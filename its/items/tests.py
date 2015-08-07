from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.core import mail
from model_mommy.mommy import make
from its.users.models import User
from its.items.models import Item, Location, Category, Action, Status
from its.items.forms import AdminActionForm, AdminItemFilterForm, ItemFilterForm, ItemArchiveForm, CheckInForm, check_ldap
from its.backends import ITSBackend
from unittest.mock import patch, Mock



def create_user():

    """
    Creates a blank lab attendant user.
    """

    user = make(User, is_active=True)
    user.set_password("password")
    user.save()
    return user


def create_full_user(first_name, last_name, email):

    """
    Creates a full customer user
    """

    user = make(User, first_name=first_name, last_name=last_name, email=email, is_active=False, is_staff=False)
    user.set_password("password")
    user.save()
    return user


def create_staff():

    """
    Creates a blank staff user.
    """

    user = make(User, is_active=True, is_staff=True)
    user.set_password("password")
    user.save()
    return user


class ITSBackendTest(TestCase):
    
    def test_get_or_init_user(self):

        # This test failed on old code, now passes.
        
        # Provide a username that doesn't exist in the database.
        # But is in one of the qualified user groups.
        
        # This code will fail if this user is no longer in ldap or has
        # been removed from groups in backends.py
        username = "will"
        User = get_user_model()
        
        ITSBackend.get_or_init_user(self, username)
        ITSBackend.get_or_init_user(self, username)

        self.assertEqual(1, User.objects.all().count())
        
        

    
class PrintoffTest(TestCase):

    def test_login_required(self):

        """
        Tests that the view sends the unauthenticated user to the login page.
        """

        response = self.client.get(reverse("printoff", args=[1]))
        self.assertRedirects(response, reverse("login") + "?next=/items/1/", target_status_code=302)

    def test_get(self):

        """
        Tests that the view returns a page with the correct item information.
        """

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

        """
        Tests that the view sends the unauthenticated user to the login page.
        """

        response = self.client.get(reverse("checkin"))
        self.assertRedirects(response, reverse("login") + "?next=/items/checkin", target_status_code=302)

    def test_get(self):

        """
        Tests that the view returns the checkin page.
        """

        user = create_user()
        self.client.login(username=user.username, password="password")

        response = self.client.get(reverse("checkin"))
        self.assertEqual(200, response.status_code)

    def test_valid_post(self):

        """
        Tests that the view sends the user to the print off page after
        a successful form submission.
        """

        user = create_user()
        self.client.login(username=user.username, password="password")

        with patch("its.items.views.CheckInForm.is_valid", return_value=True):
            with patch("its.items.views.CheckInForm.save", return_value=Mock(pk=123)) as save:
                data = {"foo": "bar"}
                response = self.client.post(reverse("checkin"), data)
                self.assertTrue(save.call_args[1]['current_user'] == user)
                self.assertRedirects(response, reverse("printoff", args=[123]), target_status_code=404)

    def test_invalid_post(self):

        """
        Tests that the view sends the user back to the checkin page if
        they enter invalid data.
        """

        user = create_user()
        self.client.login(username=user.username, password="password")

        with patch("its.items.views.CheckInForm.is_valid", return_value=False):
            data = {"foo": "bar"}
            response = self.client.post(reverse("checkin"), data)
            self.assertEqual(response.status_code, 200)


class ItemlistTest(TestCase):

    fixtures = ["actions.json"]

    def test_login_required(self):

        """
        Tests that the view sends the unauthenticated user to the login page.
        """

        response = self.client.get(reverse("itemlist"))
        self.assertRedirects(response, reverse("login") + "?next=/items/itemlist", target_status_code=302)

    def test_initial_get(self):

        """
        Tests that the view sends an authenticated user to the itemlist page.
        """

        user = create_user()
        self.client.login(username=user.username, password="password")

        response = self.client.get(reverse("itemlist"))
        self.assertEqual(200, response.status_code)

    def test_filter_get(self):

        """
        Tests that the view directs the user to the itemlist page
        after a filtering event.
        """

        user = create_user()
        self.client.login(username=user.username, password="password")

        new_location = make(Location)
        new_category = make(Category)
        new_item = make(Item, location=new_location, category=new_category)
        new_action = Action.objects.get(machine_name=Action.CHECKED_IN)
        make(Status, item=new_item, action_taken=new_action)

        data = {'select_location': new_location.pk,
                'select_category': new_category.pk, }

        response = self.client.get(reverse("itemlist"), data)
        self.assertEqual(200, response.status_code)
        self.assertIn(new_item.description, response.content.decode())


class AdminActionTest(TestCase):

    def test_login_required(self):

        """
        Tests that the view sends the unauthenticated user to the login page.
        """

        response = self.client.get(reverse("admin-action", args=[1]))
        self.assertRedirects(response, reverse("login") + "?next=/items/admin-action/1/", target_status_code=302)

    def test_get(self):

        """
        Tests that the view returns the admin action page with the correct item information.
        """

        user = create_staff()
        self.client.login(username=user.username, password="password")

        new_item = make(Item)
        make(Status, item=new_item)

        response = self.client.get(reverse("admin-action", args=[new_item.pk]))
        self.assertEqual(200, response.status_code)
        self.assertIn(new_item.description, response.content.decode())


class AdminItemlistTest(TestCase):

    def test_staff_required(self):

        """
        Tests that the view sends unauthenticated users to the login page.
        """

        response = self.client.get(reverse('admin-itemlist'))
        self.assertRedirects(response, reverse("login") + "?next=/items/admin-itemlist", target_status_code=302)

    def test_initial_get(self):

        """
        Tests that the initial retrieval of the admin-itemlist page is correct
        """

        user = create_staff()
        self.client.login(username=user.username, password="password")

        response = self.client.get(reverse("admin-itemlist"))
        self.assertEqual(200, response.status_code)

    def test_blank_post(self):

        """
        Tests that the view returns the user to the admin itemlist page
        when a blank post request is made.
        """

        user = create_staff()
        self.client.login(username=user.username, password="password")

        request = self.client.post(reverse("admin-itemlist"))
        self.assertRedirects(request, reverse("admin-itemlist"))

    def test_valid_archive_post(self):

        """
        Tests that the view returns the user to the admin itemlist page
        when a valid form is submitted.
        """

        user = create_staff()
        self.client.login(username=user.username, password="password")

        with patch('its.items.views.ItemArchiveForm.is_valid', return_value=True):
            with patch('its.items.views.ItemArchiveForm.save', return_value=True):
                form = {'test': 'data'}

                request = self.client.post(reverse("admin-itemlist"), form)
                self.assertRedirects(request, reverse("admin-itemlist"))

    def test_invalid_archive_post(self):

        """
        Tests that the view returns the user to the admin itemlist page
        when an invalid form is submitted.
        """

        user = create_staff()
        self.client.login(username=user.username, password="password")

        with patch('its.items.views.ItemArchiveForm.is_valid', return_value=False):
                form = {'test': 'data'}

                request = self.client.post(reverse("admin-itemlist"), form)
                self.assertEqual(200, request.status_code)


# Form tests

class CheckInFormTest(TestCase):

    fixtures = ["actions.json"]

    def test_clean_errors(self):

        """
        Tests that the clean method does return errors when
        the form is filled out incorrectly.
        """

        data = {
            "possible_owner_found": "1",
            "first_name": "",
            "last_name": "",
            "email": "",
            "username": "a"
        }

        with patch("its.items.forms.ModelForm.clean", return_value=data):
            with patch("its.items.forms.check_ldap", return_value=False):
                with patch("its.items.forms.CheckInForm.add_error") as add_error:
                    form = CheckInForm()
                    form.clean()
                    add_error.assert_any_call_with("first_name", "First name required")
                    add_error.assert_any_call_with("last_name", "Last name required")
                    add_error.assert_any_call_with("email", "Email required")
                    add_error.assert_any_call_with("username", "Invalid username, enter a valid username or leave blank.")

    def test_clean_no_errors(self):

        """
        Tests that the clean method does not return errors when
        the form is filled out correctly.
        """

        data = {"possible_owner_found": "1",
                "first_name": "Test",
                "last_name": "Test",
                "email": "test@test.com",
                "username": "a", }

        with patch('its.items.forms.ModelForm.clean', return_value=data):
            with patch('its.items.forms.check_ldap', return_value=True):
                form = CheckInForm()
                form.cleaned_data = form.clean()
                self.assertTrue(form.cleaned_data['possible_owner_found'] == data['possible_owner_found'])
                self.assertTrue(form.cleaned_data['username'] == data['username'])
                self.assertTrue(form.cleaned_data['first_name'] == data['first_name'])
                self.assertTrue(form.cleaned_data['last_name'] == data['last_name'])
                self.assertTrue(form.cleaned_data['email'] == data['email'])

    def test_save_new_user(self):

        """
        Tests to make sure that the save method creates a new user when it
        does not already exist in the database.
        """

        new_item = make(Item)
        new_action = Action.objects.get(machine_name=Action.CHECKED_IN)
        make(Status, action_taken=new_action, item=new_item)
        new_category = make(Category)
        new_location = make(Location)

        data = {'location': new_location,
                'category': new_category,
                'description': new_item.description,
                'is_valuable': True,
                'username': "",
                'possible_owner_found': True,
                'first_name': "test",
                'last_name': "test",
                'email': "test@test.com", }

        user = create_user()

        with patch('its.items.forms.CheckInForm.clean', return_value=data):
            form = CheckInForm(data)
            form.cleaned_data = data

            with patch("its.items.forms.ModelForm.save", return_value=new_item):
                form.save(current_user=user)

                new_user = User.objects.get(first_name=data['first_name'], last_name=data['last_name'], email=data['email'])

                self.assertTrue(data['first_name'] == new_user.first_name)
                self.assertTrue(data['last_name'] == new_user.last_name)
                self.assertTrue(data['email'] == new_user.email)

    def test_save_old_user(self):

        """
        Tests the save method to make sure it does not create a new user
        when the user already exists in the database.
        """

        new_item = make(Item)
        new_action = Action.objects.get(machine_name=Action.CHECKED_IN)
        make(Status, action_taken=new_action, item=new_item)
        new_category = make(Category)
        new_location = make(Location)

        data = {'location': new_location,
                'category': new_category,
                'description': new_item.description,
                'is_valuable': True,
                'username': "",
                'possible_owner_found': True,
                'first_name': "test",
                'last_name': "test",
                'email': "test@test.com", }

        user = create_user()
        create_full_user(data['first_name'], data['last_name'], data['email'])

        original_num_users = User.objects.all().count()

        with patch('its.items.forms.CheckInForm.clean', return_value=data):
            form = CheckInForm(data)
            form.cleaned_data = data
            with patch("its.items.forms.ModelForm.save", return_value=new_item):
                form.save(current_user=user)
                User.objects.get(first_name=data['first_name'], last_name=data['last_name'], email=data['email'])

                self.assertTrue(original_num_users == User.objects.all().count())

    def test_save_no_email(self):

        """
        Checks that an email is not sent when a non-valuable item is checked in.
        """

        new_item = make(Item, is_valuable=False)
        new_action = Action.objects.get(machine_name=Action.CHECKED_IN)
        make(Status, action_taken=new_action, item=new_item)
        new_category = make(Category)
        new_location = make(Location)

        data = {'location': new_location,
                'category': new_category,
                'description': new_item.description,
                'is_valuable': new_item.is_valuable,
                'username': "",
                'possible_owner_found': False,
                'first_name': "",
                'last_name': "",
                'email': "", }

        user = create_user()

        with patch('its.items.forms.CheckInForm.clean', return_value=data):
            form = CheckInForm(data)
            form.cleaned_data = data
            with patch("its.items.forms.ModelForm.save", return_value=new_item):
                form.save(current_user=user)

                self.assertEquals(len(mail.outbox), 0)

    def test_save_user_email(self):

        """
        Checks that an email was sent when a possible owner is indicated.
        """

        new_item = make(Item, is_valuable=False)
        new_action = Action.objects.get(machine_name=Action.CHECKED_IN)
        make(Status, action_taken=new_action, item=new_item)
        new_category = make(Category)
        new_location = make(Location)

        data = {'location': new_location,
                'category': new_category,
                'description': new_item.description,
                'is_valuable': new_item.is_valuable,
                'username': "",
                'possible_owner_found': True,
                'first_name': "test",
                'last_name': "test",
                'email': "test@test.com", }

        user = create_user()

        with patch('its.items.forms.CheckInForm.clean', return_value=data):
            form = CheckInForm(data)
            form.cleaned_data = data
            with patch("its.items.forms.ModelForm.save", return_value=new_item):
                form.save(current_user=user)

                self.assertEquals(len(mail.outbox), 1)
                self.assertEquals(mail.outbox[0].subject, 'An item belonging to you was found')

    def test_save_staff_and_user_email(self):

        """
        Checks that an email is sent to the user as well as another to staff when a valuable
        item is checked in.
        """

        new_item = make(Item, is_valuable=True)
        new_action = Action.objects.get(machine_name=Action.CHECKED_IN)
        make(Status, action_taken=new_action, item=new_item)
        new_category = make(Category)
        new_location = make(Location)

        data = {'location': new_location,
                'category': new_category,
                'description': new_item.description,
                'is_valuable': new_item.is_valuable,
                'username': "",
                'possible_owner_found': True,
                'first_name': "test",
                'last_name': "test",
                'email': "test@test.com", }

        user = create_user()

        with patch('its.items.forms.CheckInForm.clean', return_value=data):
            form = CheckInForm(data)
            form.cleaned_data = data
            with patch("its.items.forms.ModelForm.save", return_value=new_item):
                form.save(current_user=user)

                self.assertEquals(len(mail.outbox), 2)
                self.assertEquals(mail.outbox[0].subject, 'An item belonging to you was found')
                self.assertEquals(mail.outbox[1].subject, 'Valuable item checked in')


class ItemArchiveFormTest(TestCase):

    fixtures = ["actions.json"]

    def test_init(self):

        """
        Tests that the fields of the form are appended with archive fields.
        """

        user = create_staff()
        self.client.login(username=user.username, password="password")

        new_item = make(Item)
        new_action = Action.objects.get(machine_name=Action.CHECKED_IN)
        make(Status, action_taken=new_action, item=new_item)
        make(Category)
        make(Location)

        item_filter_form = AdminItemFilterForm(None)
        item_list = item_filter_form.filter()

        request = self.client.post(reverse("admin-itemlist"))

        archive_key = 'archive-' + str(new_item.pk)

        item_archive_form = ItemArchiveForm(request, item_list=item_list)
        self.assertTrue(item_archive_form.fields[archive_key])

    def test_save(self):

        """
        Checks that the archived status of items is updated.
        """

        user = create_staff()
        self.client.login(username=user.username, password="password")

        new_item = make(Item, is_archived=False)
        new_action = Action.objects.get(machine_name=Action.CHECKED_IN)
        make(Status, action_taken=new_action, item=new_item)
        make(Category)
        make(Location)

        item_filter_form = AdminItemFilterForm(None)
        item_list = item_filter_form.filter()

        request = self.client.post(reverse("admin-itemlist"))

        archive_key = 'archive-' + str(new_item.pk)

        item_archive_form = ItemArchiveForm(request, item_list=item_list)

        self.assertTrue(item_archive_form.is_valid())
        item_archive_form.cleaned_data[archive_key] = True
        item_archive_form.save()

        new_item = Item.objects.get(pk=new_item.pk)
        self.assertTrue(new_item.is_archived)

    def test_iter(self):

        """
        Checks that the iter method updates the requested page with the correct archive fields.
        """

        user = create_staff()
        self.client.login(username=user.username, password="password")

        new_item = make(Item, is_archived=False)
        new_action = Action.objects.get(machine_name=Action.CHECKED_IN)
        make(Status, action_taken=new_action, item=new_item)
        make(Category)
        make(Location)

        request = self.client.post(reverse("admin-itemlist"))

        item_filter_form = AdminItemFilterForm(None)
        item_filter_form.filter()

        request = self.client.get(reverse("admin-itemlist"))

        expected_text = "archive-" + str(new_item.pk)
        self.assertContains(request, expected_text, status_code=200, html=False)


class AdminItemFilterFormTest(TestCase):

    fixtures = ["actions.json"]

    def test_filter(self):

        """
        Test 1 - Checks that valuable items will be displayed when filtering for
        valuable items. Also Checks that searches based on location and category work.

        Test 2 - Checks that archived items are displayed when filtering for
        archived items.

        Test 3 - Checks that a non-valuable and non-archived items are displayed when filtering
        for non-valuable and non-archived items.

        Test 4 - Checks that items are sorted in the order specified.

        Test 5 - Search on last name
        """

        # Test 1 - Valuable item / Search on location and category.

        new_item1 = make(Item, is_archived=False, is_valuable=True)
        new_action = Action.objects.get(machine_name=Action.CHECKED_IN)
        make(Status, action_taken=new_action, item=new_item1)

        data = {'select_items': "valuable",
                'select_location': new_item1.location.name,
                'select_category': new_item1.category.name,
                'keyword_or_last_name': new_item1.description,
                'sort_by': '', }

        item_filter_form = AdminItemFilterForm(data)
        item_list = item_filter_form.filter()

        values = item_list.values()

        self.assertEqual(values.get()['item_id'], new_item1.pk)

        # Test 2 - Archived item

        new_item2 = make(Item, is_archived=True, is_valuable=True)

        data = {'select_items': "archived",
                'select_location': None,
                'select_category': None,
                'keyword_or_last_name': new_item2.description,
                'sort_by': '', }

        with patch('its.items.forms.AdminItemFilterForm.is_valid', return_value=True):
            item_filter_form = AdminItemFilterForm(data)
            item_filter_form.cleaned_data = data
            item_list = item_filter_form.filter()
            values = item_list.values()

            self.assertEqual(values.get()['item_id'], new_item2.pk)

        # Test 3 - not valuable, not archived item
        new_item3 = make(Item, is_archived=False, is_valuable=False)

        data = {'select_items': "",
                'select_location': None,
                'select_category': None,
                'keyword_or_last_name': new_item3.description,
                'sort_by': '', }

        with patch('its.items.forms.AdminItemFilterForm.is_valid', return_value=True):
            item_filter_form = AdminItemFilterForm(data)
            item_filter_form.cleaned_data = data
            item_list = item_filter_form.filter()
            values = item_list.values()

            self.assertEqual(values.get()['item_id'], new_item3.pk)

        # Test 4 - test item sorting
        make(Item, is_archived=False, is_valuable=False)

        data = {'select_items': "",
                'select_location': None,
                'select_category': None,
                'keyword_or_last_name': '',
                'sort_by': 'pk', }

        with patch('its.items.forms.AdminItemFilterForm.is_valid', return_value=True):
            item_filter_form = AdminItemFilterForm(data)
            item_filter_form.cleaned_data = data
            item_list = item_filter_form.filter()
            values = item_list.values()

            self.assertLess(values[0]['item_id'], values[1]['item_id'])
            self.assertLess(values[1]['item_id'], values[2]['item_id'])

        # Test 5 - Search on last name
        user = create_full_user("test", "test", "test@pdx.edu")

        new_item5 = make(Item, is_archived=False, is_valuable=False, possible_owner=user)

        data = {'select_items': "",
                'select_location': None,
                'select_category': None,
                'keyword_or_last_name': user.last_name,
                'sort_by': '', }

        with patch('its.items.forms.AdminItemFilterForm.is_valid', return_value=True):
            item_filter_form = AdminItemFilterForm(data)
            item_filter_form.cleaned_data = data
            item_list = item_filter_form.filter()
            values = item_list.values()

            self.assertEqual(values.get()['item_id'], new_item5.pk)


class ItemFilterFormTest (TestCase):

    fixtures = ["actions.json"]

    def test_filter(self):

        """
        Check that the filter displays only items with status of "Checked in"
        """

        new_item1 = make(Item, is_archived=False, is_valuable=False)
        new_action1 = Action.objects.get(machine_name=Action.CHECKED_IN)
        make(Status, action_taken=new_action1, item=new_item1)

        new_item2 = make(Item, is_archived=True, is_valuable=False)
        new_action2 = Action.objects.get(machine_name=Action.RETURNED)
        make(Status, action_taken=new_action2, item=new_item2)

        data = {'select_items': "",
                'select_location': None,
                'select_category': None,
                'keyword_or_last_name': "",
                'sort_by': 'pk', }

        item_filter_form = ItemFilterForm(data)
        item_list = item_filter_form.filter()
        values = item_list.values()

        self.assertEqual(values[0]['item_id'], new_item1.pk)
        self.assertEqual(len(values), 1)


class AdminActionFormTest (TestCase):

    fixtures = ["actions.json"]

    def test_init(self):

        """
        Test 1 - Check that regular student lab attendants only have the return option
        Test 2 - Check that staff have all admin options available to them.
        """

        # Test 1 - Lab attendant user

        user = create_user()

        form = AdminActionForm(current_user=user)
        self.assertEquals(len(form.fields), 4)

        # Test 2 - Staff user

        user = create_staff()
        total_actions = len(Action.objects.all())

        form = AdminActionForm(current_user=user)
        self.assertEqual(len(form.fields['action_choice'].queryset), total_actions)
        self.assertEquals(len(form.fields), 5)

    def test_checkout_email(self):

        """
        Check that an email is sent to the staff when a valuable
        item is returned.
        """
        user = create_staff()

        new_item = make(Item, is_valuable=True)
        new_action = Action.objects.get(machine_name=Action.RETURNED)

        data = {'action_choice': new_action,
                'note': "",
                'first_name': 'abcd',
                'last_name': '1234',
                'email': 'test@test.com', }

        with patch('its.items.forms.AdminActionForm.is_valid', return_value=True):
            form = AdminActionForm(data, current_user=user)
            form.cleaned_data = data
            form.save(item_pk=new_item.pk, current_user=user)

            self.assertEquals(len(mail.outbox), 1)
            self.assertEquals(mail.outbox[0].subject, 'Valuable item checked out')

    def test_clean_with_errors(self):

        """
        Test 1 - Check that errors appear when returning item with bad data.
        Test 2 - Check that errors appear when performing other action with bad data.
        Test 3 - Check that errors appear when action_choice is of type None.
        """

        # Test 1 - Check for errors when returning item.
        user = create_staff()

        new_action = Action.objects.get(machine_name=Action.RETURNED)

        data = {'action_choice': new_action,
                'note': "",
                'first_name': "",
                'last_name': "",
                'email': "", }

        with patch('its.items.forms.AdminActionForm.clean', return_value=data):
                with patch("its.items.forms.AdminActionForm.add_error") as add_error:
                    form = AdminActionForm(data, current_user=user)
                    form.clean()

                    add_error.assert_any_call_with("first_name", "First name is required when returning item.")
                    add_error.assert_any_call_with("last_name", "Last name is required when returning item.")
                    add_error.assert_any_call_with("email", "Email is required when returning item.")

        # Test 2 - Check for errors when selecting other action.

        new_action = Action.objects.get(machine_name=Action.OTHER)

        data = {'action_choice': new_action,
                'note': "",
                'first_name': "",
                'last_name': "",
                'email': "", }

        with patch('its.items.forms.AdminActionForm.clean', return_value=data):
                with patch("its.items.forms.AdminActionForm.add_error") as add_error:
                    form = AdminActionForm(data, current_user=user)
                    form.clean()

                    add_error.assert_any_call_with("note", "Note required when choosing action of type Other.")

        # Test 3 - Check for errors when action_choice not in dictionary.
        # Failed as NoneType AttributeError for machine_name in clean on old code.
        user = create_user()

        data = {'action_choice': None,
                'note': "",
                'first_name': "",
                'last_name': "",
                'email': "", }

        form = AdminActionForm(data, current_user=user)
        self.assertFalse(form.is_valid())

    def test_clean_no_errors(self):

        """
        Test 1 - Check that no errors appear when returning an item with correct data.
        Test 2 - Check that no errors appear when performing other action with correct data.
        """

        # Test 1 - Check for no errors when returning item.
        user = create_staff()

        new_action = Action.objects.get(machine_name=Action.RETURNED)

        data = {'action_choice': new_action,
                'note': "",
                'first_name': "abcd",
                'last_name': "1234",
                'email': "test@test.com", }

        with patch('its.items.forms.AdminActionForm.clean', return_value=data):
            form = AdminActionForm(data, current_user=user)
            form.cleaned_data = form.clean()

            self.assertTrue(form.cleaned_data['first_name'] == data['first_name'])
            self.assertTrue(form.cleaned_data['last_name'] == data['last_name'])
            self.assertTrue(form.cleaned_data['email'] == data['email'])

        # Test 2 - Check for no errors when performing other action.
        new_action = Action.objects.get(machine_name=Action.OTHER)

        data = {'action_choice': new_action,
                'note': "test",
                'first_name': "",
                'last_name': "",
                'email': "", }

        with patch('its.items.forms.AdminActionForm.clean', return_value=data):
            form = AdminActionForm(data, current_user=user)
            form.cleaned_data = form.clean()

            self.assertTrue(form.cleaned_data['note'] == data['note'])

    def test_save(self):

        """
        Test 1 - Check that the returned to field is set to None when an item
        has it's status set back to checked in

        Test 2 - Check that the returned to field is correctly set when an item
        is returned to it's owner.

        Test 3 Check that an email is sent to the staff mailing list
        when a valuable item is returned to it's owner.

        Test 4 check that a new user is made when an item is returned and that
        person did not exist in the system previously.

        Test 5 Check that an existing user does not have an account created when
        an item is returned to them.
        """

        # Test 1 Check that the returned to field is set to None when an item
        # has it's status set back to checked in

        user = create_staff()

        new_item = make(Item, is_valuable=False)
        new_action = Action.objects.get(machine_name=Action.CHECKED_IN)

        data = {'action_choice': new_action,
                'note': "",
                'first_name': "",
                'last_name': "",
                'email': "", }

        with patch('its.items.forms.AdminActionForm.is_valid', return_value=True):
            with patch('its.items.forms.AdminActionForm.clean', return_value=data):

                form = AdminActionForm(data, current_user=user)
                form.cleaned_data = form.clean()
                form.save(item_pk=new_item.pk, current_user=user)
                new_item = Item.objects.get(pk=new_item.pk)
                self.assertIsNone(new_item.returned_to)

        # Test 2 Check that the returned to field is correctly set when an item
        # is returned to it's owner.
        new_action = Action.objects.get(machine_name=Action.RETURNED)

        data = {'action_choice': new_action,
                'note': "",
                'first_name': "abcd",
                'last_name': "1234",
                'email': "test@test.com", }

        with patch('its.items.forms.AdminActionForm.is_valid', return_value=True):
            with patch('its.items.forms.AdminActionForm.clean', return_value=data):

                form = AdminActionForm(data, current_user=user)
                form.cleaned_data = form.clean()
                form.save(item_pk=new_item.pk, current_user=user)
                new_item = Item.objects.get(pk=new_item.pk)
                self.assertIsNotNone(new_item.returned_to)

        # Test 3 Check that an email is sent to the staff mailing list
        # when a valuable item is returned to it's owner.

        new_item = make(Item, is_valuable=True)

        data = {'action_choice': new_action,
                'note': "",
                'first_name': "abcd",
                'last_name': "1234",
                'email': "test@test.com", }

        with patch('its.items.forms.AdminActionForm.is_valid', return_value=True):
            with patch('its.items.forms.AdminActionForm.clean', return_value=data):

                form = AdminActionForm(data, current_user=user)
                form.cleaned_data = form.clean()
                form.save(item_pk=new_item.pk, current_user=user)

                self.assertEquals(len(mail.outbox), 1)
                self.assertEquals(mail.outbox[0].subject, 'Valuable item checked out')

        # Test 4 check that a new user is made when an item is returned and that
        # person did not exist in the system previously.

        data = {'action_choice': new_action,
                'note': "",
                'first_name': "test",
                'last_name': "1234",
                'email': "test@test.com", }

        try:
            user_search = User.objects.get(first_name=data["first_name"])
        except User.DoesNotExist:
            user_search = None

        self.assertIsNone(user_search)

        with patch('its.items.forms.AdminActionForm.is_valid', return_value=True):
            with patch('its.items.forms.AdminActionForm.clean', return_value=data):

                form = AdminActionForm(data, current_user=user)
                form.cleaned_data = form.clean()
                form.save(item_pk=new_item.pk, current_user=user)

                try:
                    user_search = User.objects.get(first_name=data["first_name"])
                except User.DoesNotExist:
                    user_search = None

                self.assertIsNotNone(user_search)

        # Test 5 Check that an existing user does not have an account created when
        # an item is returned to them.

        num_users = User.objects.all().count()

        with patch('its.items.forms.AdminActionForm.is_valid', return_value=True):
            with patch('its.items.forms.AdminActionForm.clean', return_value=data):

                form = AdminActionForm(data, current_user=user)
                form.cleaned_data = form.clean()
                form.save(item_pk=new_item.pk, current_user=user)

                self.assertEqual(num_users, User.objects.all().count())


# Helper function tests

class checkLdapTest(TestCase):

    def test_ldap_return_true(self):

        """
        Check that the correct value of True is returned for a username
        that is in LDAP.
        """

        with patch('its.items.forms.ldapsearch', return_value=True):
            user = check_ldap("test12345")
            self.assertTrue(user)

    def test_ldap_return_false(self):

        """
        Check that the correct value of False is returned for a username that
        is not in LDAP.
        """

        with patch('its.items.forms.ldapsearch', return_value=False):
            user = check_ldap("test12345")
            self.assertFalse(user)
