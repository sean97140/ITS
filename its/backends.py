from djangocas.backends import CASBackend
from django.contrib.auth import get_user_model
from arcutils.ldap import ldapsearch
import arcutils.ldap
import re

class ITSBackend(CASBackend):   

    def create_user(new_first_name, new_last_name, new_email):

        """
        Generates a unique user name.
        """
    
        new_username = '_' + new_first_name + new_last_name
        i = 0
            
        while User.objects.filter(username=new_username + str(i)).exists():
            i += 1
                
        new_username = new_username + str(i)                 
        new_user = User(first_name = new_first_name, last_name = new_last_name, 
        email = new_email, username = new_username, is_active=False, is_staff=False)
                
        new_user.save()
    
        return new_user

    #Override
    def get_or_init_user(self, username):
        query = "(cn=" + username + ")"
    
        results = ldapsearch(query, using='groups')
        memberOf = results[0][1]['memberOf']
        first_name = str(results[0][1]['givenName'])
        last_name = str(results[0][1]['sn'])
        email = str(results[0][1]['mail'])
        
        staff = False
        student = False
        
        if re.search("(CN=ITS_CAVS_Staff_GG)", str(memberOf)):
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
        
        
      