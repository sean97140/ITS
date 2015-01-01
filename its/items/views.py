from django.shortcuts import render, get_object_or_404
from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from its.items.models import Item, Location, Category, Status, Action
from its.users.models import User
from its.items.forms import CheckInForm
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse
from arcutils.ldap import escape, ldapsearch, parse_profile
from django.views.generic import ListView

def itemlist(request):
    item_list = Item.objects.order_by('-pk')
    context = {'items': item_list}
    return render(request, 'items/itemlist.html', context)


"""
def admin(request):

    if request.method == 'POST':
        form = AdminForm(request.POST)
        
        if form.is_valid():
            print("nothing yet")
            
    else:
        form = AdminForm()
        
    return render(request, 'items/admin.html', {'form': form})
"""
        

def checkin(request):
    if request.method == 'POST':
        form = CheckInForm(request.POST)
		
        if form.is_valid():            
            new_item = form.save(found_by=request.user)	
            return HttpResponseRedirect(reverse("printoff", args = [new_item.pk]))
			
    else:
        form = CheckInForm()
		
    return render(request, 'items/checkin.html', {'form': form})

    
"""Does an LDAP search and returns a JSON array of objects"""
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
    
    
def printoff(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'items/printoff.html', {'item': item})
	