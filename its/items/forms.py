from django import forms
from django.conf import settings
from django.forms import ModelForm
from its.users.models import User
from its.items.models import Item, Location, Category, Status, Action
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from arcutils.ldap import escape, ldapsearch
from django.db.models import Q


def check_ldap(username):

    """
    Checks LDAP to ensure a user name exists.
    """

    q = escape(username)
    search = '(uid={q}*)'.format(q=q)
    results = ldapsearch(search)

    if results:
        return True

    else:
        return False


def create_user(new_first_name, new_last_name, new_email):

    """
    Generates a unique user name.
    """

    new_username = '_' + new_first_name + new_last_name
    i = 0

    while User.objects.filter(username=new_username + str(i)).exists():
        i += 1

    new_username = new_username + str(i)
    new_user = User(first_name=new_first_name, last_name=new_last_name,
                    email=new_email, username=new_username, is_active=False, is_staff=False)

    new_user.save()

    return new_user


class AdminActionForm(forms.Form):

    """
    Form used on the admin-action page
    """

    action_choice = forms.ModelChoiceField(queryset=Action.objects.all(), required=True, empty_label=None)
    note = forms.CharField(widget=forms.Textarea, required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    def __init__(self, *args, user, **kwargs):

        """
        Allow only the return option to be selected by lab attendants.
        """

        self.user = user
        super(AdminActionForm, self).__init__(*args, **kwargs)

        if not self.user.is_staff:
            self.fields['action_choice'].queryset = self.fields['action_choice'].queryset.filter(machine_name=Action.RETURNED)

    def checkout_email(self, item):

        """
        Send an email to all the admins when a valuable item is checked out
        """
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

    def clean(self):

        """
        Require note field on action of OTHER
        """

        cleaned_data = super().clean()
        action_choice = cleaned_data.get("action_choice")
        note = cleaned_data.get("note")
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        email = cleaned_data.get("email")

        if (action_choice.machine_name == Action.RETURNED) and not first_name:
            self.add_error("first_name", "First name is required when returning item.")

        if (action_choice.machine_name == Action.RETURNED) and not last_name:
            self.add_error("last_name", "Last name is required when returning item.")

        if (action_choice.machine_name == Action.RETURNED) and not email:
            self.add_error("email", "Email is required when returning item.")

        if (action_choice.machine_name == Action.OTHER) and not note:
            self.add_error("note", "Note required when choosing action of type Other.")

        return cleaned_data

    def save(self, *args, item_pk, current_user, **kwargs):

        """
        If an item is being returned, create a new user for the person the item is being
        returned to if they don't already exist. Then send an email to the staff mailing
        list if the item is valuable.

        If an item is being set to checked in set it's returned_to field to None.
        """

        action_choice = self.cleaned_data["action_choice"]
        item = Item.objects.get(pk=item_pk)
        first_name = self.cleaned_data.get("first_name")
        last_name = self.cleaned_data.get("last_name")
        email = self.cleaned_data.get("email")
        new_action = Action.objects.get(name=self.cleaned_data['action_choice'])
        new_status = Status(item=item, action_taken=new_action, note=self.cleaned_data['note'], performed_by=current_user).save()

        # If they chose to change status to checked in we need to make sure to
        # set the returned_to field to None
        if action_choice.machine_name == Action.CHECKED_IN:
            item.returned_to = None

        if action_choice.machine_name == Action.RETURNED:

            try:
                returned_user = User.objects.get(first_name=first_name, last_name=last_name, email=email)
            except User.DoesNotExist:
                returned_user = create_user(first_name, last_name, email)

            item.returned_to = returned_user

            if(item.is_valuable is True):
                self.checkout_email(item)

        item.save()
        return item


class AdminItemFilterForm(forms.Form):

    """
    Administrative item filter form for the admin itemlist page
    """

    sort_choices = (
        ('-pk', 'Found most recently'),
        ('pk', 'Found least recently'),
        ('location', 'Location'),
        ('category', 'Category'),
        ('description', 'Description'),
        ('possible_owner', 'Possible owner'),
    )

    admin_item_choices = (
        ('active', 'Active'),
        ('archived', 'Archived only'),
        ('valuable', 'Valuable only'),
    )

    select_location = forms.ModelChoiceField(queryset=Location.objects.all(), required=False)
    select_category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    sort_by = forms.ChoiceField(choices=sort_choices, required=False)
    select_items = forms.ChoiceField(choices=admin_item_choices, required=False, initial=admin_item_choices[0][0])
    keyword_or_last_name = forms.CharField(max_length=50, required=False)

    def filter(self):

        """
        Setup a filter, depending on if the user chose to filter by an active, archived, or valuable items.
        As well as by choice of location category, or keyword. The user can also select a sorting order.
        """
        keyword_search = None
        kwargs = {}

        valid = False

        # Setup the filter with the users selections
        if self.is_valid():

            valid = True

            if self.cleaned_data['select_items'] == 'valuable':
                kwargs['is_valuable'] = True

            elif self.cleaned_data['select_items'] == "archived":
                kwargs['is_archived'] = True

            else:
                kwargs['is_archived'] = False

            if self.cleaned_data['select_location'] is not None:
                kwargs['location'] = Location.objects.get(name=self.cleaned_data['select_location']).pk

            if self.cleaned_data['select_category'] is not None:
                kwargs['category'] = Category.objects.get(name=self.cleaned_data['select_category']).pk

            if self.cleaned_data['keyword_or_last_name'] is not '':
                keyword_search = Q(description__icontains = self.cleaned_data['keyword_or_last_name']) | Q(possible_owner__last_name__icontains = self.cleaned_data['keyword_or_last_name'])
				
        else:
            kwargs['is_archived'] = False

        if keyword_search:
            item_list = Item.objects.filter(keyword_search, **kwargs).order_by('-pk')

        else:
            item_list = Item.objects.filter(**kwargs).order_by('-pk')

        if valid and self.cleaned_data['sort_by'] is not '':
            item_list = item_list.order_by(self.cleaned_data['sort_by'])

        return item_list


class ItemFilterForm(AdminItemFilterForm):

    """
    Item filter form for the regular itemlist page
    """

    item_choices = (
        ('active', 'Active'),
        ('valuable', 'Valuable only'),
    )

    select_items = forms.ChoiceField(choices=item_choices, required=False, initial=item_choices[0][0])

    def filter(self):

        """
        Update the filter so that lab attendants can only see items with the statsu of CHECKED_IN
        """

        item_list = super(ItemFilterForm, self).filter()
        item_list = item_list.select_related("last_status").filter(laststatus__machine_name=Action.CHECKED_IN)

        return item_list


class ItemArchiveForm(forms.Form):

    """
    Item archiving form used on the administrative item listing page.
    """

    def __init__(self, *args, item_list, **kwargs):

        """
        Setup a pre-filled checkbox, based on the item's current archived status.
        """
        super(ItemArchiveForm, self).__init__(*args, **kwargs)

        self.item_list = item_list
        for item in item_list:
            self.fields['archive-%d' % item.pk] = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'checkbox_archive'}), initial=item.is_archived, required=False)

    def __iter__(self):

        """
        when iterating over this form, add archive-item.pk to each item.
        """

        for item in self.item_list:
            yield item, self['archive-%d' % item.pk]

    def save(self):

        """
        If an item is in the list, swap the items archived status.
        """

        changed = False

        for item in self.item_list:
            is_archived = self.cleaned_data.get("archive-%d" % item.pk)

            if item.is_archived is not is_archived:
                item.is_archived = is_archived
                item.save()
                changed = True

        return changed


class CheckInForm(ModelForm):

    """
    Form for the checkin view
    """

    possible_owner_found = forms.BooleanField(required=False)
    username = forms.CharField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

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

        """
        Send an email to a possible owner when an item they own is checked in
        """

        subject = 'An item belonging to you was found'
        to = [possible_owner.email]
        from_email = settings.CHECKIN_EMAIL_FROM

        ctx = {
            'possible_owner_name': str(item.possible_owner),
            'found_in': item.location.name,
        }

        if item.category.machine_name == Category.USB:
            message = render_to_string('items/user_checkin_email_usb.txt', ctx)

        elif item.category.machine_name == Category.ID:
            message = render_to_string('items/user_checkin_email_id.txt', ctx)

        else:
            message = render_to_string('items/user_checkin_email_all_other.txt', ctx)

        EmailMessage(subject, message, to=to, from_email=from_email).send()

    def clean(self):

        """
        If a possible owner has been found, force the person
        to provide a first name, last name, and email.
        """

        cleaned_data = super(CheckInForm, self).clean()
        username = cleaned_data.get("username")
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        email = cleaned_data.get("email")
        possible_owner_found = cleaned_data.get("possible_owner_found")

        # If possilbe owner found is checked we need to make these
        # optional fields required.
        if possible_owner_found and not first_name:
            self.add_error("first_name", "First name required")

        if possible_owner_found and not last_name:
            self.add_error("last_name", "Last name required")

        if possible_owner_found and not email:
            self.add_error("email", "Email required")

        if possible_owner_found and username and not check_ldap(username):
            self.add_error("username", "Invalid username, enter a valid username or leave blank.")

        return cleaned_data

    def save(self, *args, current_user, **kwargs):

        """
        If a possible owner has been found send them an email.
        If an item is valuable send the staff mailing list an email.
        """
        user_first_name = self.cleaned_data['first_name']
        user_last_name = self.cleaned_data['last_name']
        user_email = self.cleaned_data['email']

        # If an owner was found we need to record them as an owner
        # This may require that a new user is created
        if self.cleaned_data.get("possible_owner_found") is True:

            try:
                checkin_user = User.objects.get(first_name=user_first_name, last_name=user_last_name, email=user_email)
            except User.DoesNotExist:
                checkin_user = create_user(user_first_name, user_last_name, user_email)

            self.instance.possible_owner = checkin_user

        item = super(CheckInForm, self).save(*args, **kwargs)

        new_action = Action.objects.get(machine_name=Action.CHECKED_IN)
        new_status = Status(item=item, action_taken=new_action, note="Initial check-in", performed_by=current_user).save()

        if(self.cleaned_data['email'] != ''):
            self.user_checkin_email(item, checkin_user)

        if(self.cleaned_data['is_valuable'] is True):
            self.checkin_email(item)

        return item

    class Meta:
        model = Item
        fields = ['location', 'category', 'description', 'is_valuable',
                  'possible_owner_contacted']
