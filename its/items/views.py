from django.shortcuts import render, get_object_or_404
from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from its.items.models import Item, Location, Category, Status, Action
from its.users.models import User
from its.items.forms import CheckInForm, ItemFilterForm, ItemArchiveForm, AdminItemFilterForm, AdminActionForm
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse
from arcutils.ldap import escape, ldapsearch, parse_profile
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

   
@staff_member_required
def admin_itemlist(request):
 
    """
    Administrative item listing, allows for viewing of items, 
    taking actions on items, and archiving items. 
    """
     
    # Built item list from filter.
    item_filter_form = AdminItemFilterForm(request.GET if "action" in request.GET else None)
    item_list = item_filter_form.filter()

        
    # Process archive request
    if request.method == 'POST':
        
        item_archive_form = ItemArchiveForm(request.POST, item_list=item_list)
        
        if item_archive_form.is_valid():
            item_archive_form.save()
            messages.success(request, "Item successfully changed")
            return HttpResponseRedirect(request.get_full_path())
    
    else:
        item_archive_form = ItemArchiveForm(item_list=item_list)
        
    return render(request, 'items/admin-itemlist.html', {
        'items': item_list, 
        'item_filter': item_filter_form,
        'archive_form': item_archive_form,
        })

       
@login_required
def adminaction(request, item_num):
    
    """
    Administrative action page
    Allows user to change status of items.  
    """
    current_user = request.user
    chosen_item = get_object_or_404(Item, pk=item_num)
    status_list = Status.objects.filter(item=item_num)
    
    # Perform action on item
    if request.method == 'POST':
    
        form = AdminActionForm(request.POST, user=request.user)
        
        if form.is_valid():
            messages.success(request, "Item successfully changed")
            form.save(item_pk=item_num, current_user=request.user)	
            return HttpResponseRedirect(reverse("admin-itemlist"))
    
    else:
        form = AdminActionForm(user=request.user)
    
    context = {'item': chosen_item,
               'form': form,
               'status_list': status_list}

    return render(request, 'items/admin-action.html', context)


@login_required
def itemlist(request):
    
    """
    Non-administrative item listing
    Can view item list and return items    
    """
        
    # Create and filter item list
    item_filter_form = ItemFilterForm(request.GET if "action" in request.GET else None)
    item_list = item_filter_form.filter()

    return render(request, 'items/itemlist.html', {
        'items': item_list,
        'item_filter': item_filter_form,
        })


@login_required
def checkin(request):
    
    """        
    Item check in form
    Allows lab attendant to check an item into inventory.       
    """
    
    if request.method == 'POST':
        form = CheckInForm(request.POST)
		
        if form.is_valid():            
            new_item = form.save(current_user=request.user)	
            return HttpResponseRedirect(reverse("printoff", args=[new_item.pk]))
			
    else:
        form = CheckInForm()
		
    return render(request, 'items/checkin.html', {'form': form})

    

@login_required
def autocomplete(request):
    
    """
    Does an LDAP search and returns a JSON array of objects
    """

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
    
    """
    Item check in print off page
    Page lab attends should print off when they check in an item in.
    """
    
    if request.method == 'POST' and request.POST['action'] == "Return to item check-in":
        return HttpResponseRedirect(reverse("checkin"))
        
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'items/printoff.html', {'item': item})
	
