function toggleReturnFields() {

        var current_choice = $('#id_action_choice :selected').text();
        
        if(current_choice == "Returned") {
            $(".returnFields").slideDown("fast");
        }
        else {
           $(".returnFields").slideUp("fast");  
        }
    
}

$(function(){

    toggleReturnFields();

    $('#id_action_choice').change(toggleReturnFields);
   
}); 