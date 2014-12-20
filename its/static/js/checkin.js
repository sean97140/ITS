$(function(){
    
   // jQuery methods go here...
   
   // hides the element with id="username".
   $('label[for=id_username]').toggle();
   $('label[for=id_first_name]').toggle();
   $('label[for=id_last_name]').toggle();
   $('label[for=id_email]').toggle();
   $('label[for=id_phone]').toggle();
   
   // hides all elements with class="NewUserClass".
   $(".NewUserClass").toggle() 
   
   $('#id_possible_owner_contacted').click(function() {
   
      // shows the element with id="username".
      $('label[for=id_username]').toggle();
      $('label[for=id_first_name]').toggle();
      $('label[for=id_last_name]').toggle();
      $('label[for=id_email]').toggle();
      $('label[for=id_phone]').toggle();
   
      // shows all elements with class="NewUserClass".
      $(".NewUserClass").toggle() 
   
   })

   
   
}); 