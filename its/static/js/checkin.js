$(function(){
    
   // jQuery methods go here...
   // hides the element with id="username".
   $(".PossibleOwner").toggle() 
   
   $('#id_possible_owner_found').click(function() {
      $(".PossibleOwner").toggle() 
   })
   
   // $('#id_username').on('blur', function() {
   //     alert('Handler for .blur() called.');
   // });
}); 