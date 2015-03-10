from django.shortcuts import render, get_object_or_404
from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from its.items.models import Item, Location, Category, Status, Action
from its.users.models import User
from its.items.forms import CheckInForm, ItemFilterForm, AdminItemFilterForm, ItemSelectForm, ItemReturnForm, AdminActionForm
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse
from arcutils.ldap import escape, ldapsearch, parse_profile
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

@staff_member_required
def view_item(request, item_num):    
        
    chosen_item = get_object_or_404(Item, pk=item_num)
    status_list = Status.objects.filter(item=item_num)
    context = {'item': chosen_item,
               'status_list': status_list}

    return render(request, 'items/view_item.html', context)

    
@staff_member_required
def admin_itemlist(request):

    if request.method == 'POST' and request.POST['action'] == "Archive selected items":
        #import pdb; pdb.set_trace()
        
        choices = request.POST.getlist('choices')
        
        for choice in choices:
            item = Item.objects.get(pk=choice)
            item.is_archived = True
            item.save()
        
        return HttpResponseRedirect(reverse("admin-itemlist"))
        
        
    if request.method == 'GET' and request.GET.get('action') == "Reset":
        
        item_filter_form = AdminItemFilterForm()   
        item_list = Item.objects.order_by('-pk')
    
    if request.method == 'GET' and request.GET.get('action') == "Filter":
		
        form = AdminItemFilterForm(request.GET)
        
        if form.is_valid() and (form.cleaned_data['select_location'] is not None or form.cleaned_data['select_category'] is not None or form.cleaned_data['display_is_valuable_only'] is not False or form.cleaned_data['search_keyword_or_name'] is not None):
            
            kwargs = {}
            
            if form.cleaned_data['display_archived_only'] is True:
                kwargs['is_archived'] = True
                
            if form.cleaned_data['display_is_valuable_only'] is True:
                kwargs['is_valuable'] = True
            
            if form.cleaned_data['select_location'] is not None:
                kwargs['location'] = Location.objects.get(name=form.cleaned_data['select_location']).pk
                
            if form.cleaned_data['select_category'] is not None:
                kwargs['category'] = Category.objects.get(name=form.cleaned_data['select_category']).pk
            
            if form.cleaned_data['search_keyword_or_name'] is not '':
                kwargs['description'] = form.cleaned_data['search_keyword_or_name']
            
            item_list = Item.objects.filter(**kwargs)
            if form.cleaned_data['sort_by'] is not '':
                item_list = item_list.order_by(form.cleaned_data['sort_by'])

            item_filter_form = AdminItemFilterForm(request.GET)   
        
    else:
        
        item_filter_form = AdminItemFilterForm()   
        item_list = Item.objects.filter(is_archived=False).order_by('-pk')
    
    return render(request, 'items/admin-itemlist.html', {
        'items': item_list, 
        'ItemFilter': item_filter_form,
        })

        
@staff_member_required
def adminaction(request, item_num):
    
    chosen_item = get_object_or_404(Item, pk=item_num)

    if request.method == 'POST' and request.POST['action'] == "Cancel":
        return HttpResponseRedirect(reverse("admin-itemlist"))
    
    if request.method == 'POST' and request.POST['action'] == "Perform action":
    
        #import pdb; pdb.set_trace()
    
        form = AdminActionForm(request.POST)
        
        if form.is_valid():

            form.save(item_pk=item_num, current_user=request.user)	
            return HttpResponseRedirect(reverse("admin-itemlist"))
    
    else:
        form = AdminActionForm()
        
    return render(request, 'items/admin-action.html', {'form': form, 'item': chosen_item})

    
@login_required
def checkout(request, item_num):
    
    
    if request.method == 'POST':
    
        if request.POST['action'] == 'Cancel':
            return HttpResponseRedirect(reverse("itemlist"))
        
        if request.POST['action'] == "Return Item":
    
            form = ItemReturnForm(request.POST)
        
            if form.is_valid():
                messages.success(request, "Item successfully returned")
                form.save(item_pk=item_num, performed_by=request.user)	
                return HttpResponseRedirect(reverse("itemlist"))
    
    chosen_item = get_object_or_404(Item, pk=item_num)
    form = ItemReturnForm()
        
    return render(request, 'items/checkout.html', {'form': form, 'item': chosen_item})

    
@login_required
def itemlist(request):


    if request.method == 'GET' and request.GET.get('action') == "Reset":
        
        item_filter_form = ItemFilterForm()   
        item_list = Item.objects.order_by('-pk')
    
    if request.method == 'GET' and request.GET.get('action') == "Filter":
        
        form = ItemFilterForm(request.GET)
		
        if form.is_valid() and (form.cleaned_data['select_location'] is not None or form.cleaned_data['select_category'] is not None or form.cleaned_data['display_is_valuable_only'] is not False or form.cleaned_data['search_keyword_or_name'] is not None):
            
            kwargs = {}
            
            if form.cleaned_data['display_is_valuable_only'] is True:
                kwargs['is_valuable'] = True
            
            if form.cleaned_data['select_location'] is not None:
                kwargs['location'] = Location.objects.get(name=form.cleaned_data['select_location']).pk
                
            if form.cleaned_data['select_category'] is not None:
                kwargs['category'] = Category.objects.get(name=form.cleaned_data['select_category']).pk
            
            if form.cleaned_data['search_keyword_or_name'] is not '':
                kwargs['description'] = form.cleaned_data['search_keyword_or_name']
            
            item_list = Item.objects.filter(**kwargs).select_related("last_status").filter(laststatus__machine_name="CHECKED_IN")
            
            if form.cleaned_data['sort_by'] is not '':
                item_list = item_list.order_by(form.cleaned_data['sort_by'])

            item_filter_form = ItemFilterForm(request.GET)   
  
    else:
        
        item_filter_form = ItemFilterForm()   
        item_list = Item.objects.filter().select_related("last_status").filter(laststatus__machine_name="CHECKED_IN").order_by('-pk')

    return render(request, 'items/itemlist.html', {
        'items': item_list,
        'ItemFilter': item_filter_form,
        })

        
@login_required
def checkin(request):

    if request.method == 'POST':
        form = CheckInForm(request.POST)
		
        if form.is_valid():            
            new_item = form.save(current_user=request.user)	
            return HttpResponseRedirect(reverse("printoff", args=[new_item.pk]))
			
    else:
        form = CheckInForm()
		
    return render(request, 'items/checkin.html', {'form': form})

    
"""Does an LDAP search and returns a JSON array of objects"""
@login_required
def autocomplete(request):
    q = escape(request.GET['query'])
    search = '(& (| (uid={q}*) (cn={q}*)) (psuprivate=N))'.format(q=q)
    results = ldapsearch(search)
    # I don't think LDAP guarantees the sort order, so we have to sort ourselves
    results.sort(key=lambda o: o[1]['uid'][0])
    output = []
    # only return a handful of results
    MAX_RESULTS = 10
    
    for result in results[:MAX_RESULTS]:
        output.append(parse_profile(result[1]))
        
    return JsonResponse(output, safe=False)
    

@login_required
def printoff(request, item_id):
    
    if request.method == 'POST' and request.POST['action'] == "Return to item check-in":
        return HttpResponseRedirect(reverse("checkin"))
        
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'items/printoff.html', {'item': item})
	
