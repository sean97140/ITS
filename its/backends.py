from djangocas.backends import CASBackend
from django.contrib.auth import get_user_model
from arcutils.ldap import ldapsearch, parse_profile
from its.items.forms import create_user
import re

class ITSBackend(CASBackend):   

    """
    Custom backend, allows for use of CAS and AD user lookups.
    """


    #Override
    def get_or_init_user(self, username):

        query = "(cn=" + username + ")"
        results = ldapsearch(query, using='groups')
        
        # Get the list of groups that the user belongs too.
        memberOf = results[0][1]['memberOf']
        
        # Add the username as a list for the uid dictionary key.
        results[0][1]['uid'] = [username]
        
        user_info = parse_profile(results[0][1])
        first_name = user_info['first_name']
        last_name = user_info['last_name']
        email = user_info['email']
        
        staff = False
        student = False
        
        if re.search("(CN=ITS_LAB_Students_GG)", str(memberOf)):
            student = True
        
        if re.search("(CN=ITS_CAVS_Staff_GG)", str(memberOf)):
            staff = True
            
        if re.search("(OU=ARC)", str(memberOf)):
            staff = True
        
        # Remove this in production
        if re.search("(CN=pbt)", str(results)):
            staff = True
            
        if student or staff:
            User = get_user_model()
            
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = create_user(first_name, last_name, email)
            
            # Always need to reset the users permissions, to stay up to date with
            # group changes.
            user.is_active = False
            user.is_staff = False
            user.save()
            
            if staff:
                user.is_active = True
                user.is_staff = True
                user.save()
            
            if student:
                user.is_active = True
                user.save()
        
            return user
         
        else:
            return None
        
        
      