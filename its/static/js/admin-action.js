function toggleReturnFields() {


        if($('#id_action_choice').length > 0)
        {
            var current_choice = $('#id_action_choice :selected').text();
        
            if(current_choice == "Returned") {
                $(".returnFields").slideDown("fast");
            }
            else {
                $(".returnFields").hide();  
            }
            
        }

}

$(function(){

    toggleReturnFields();

    $('#id_action_choice').change(toggleReturnFields);
   
}); 