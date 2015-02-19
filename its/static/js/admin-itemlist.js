$(function() {

  var masterCheckbox = $('#select_all');
  var slaveCheckboxes = $('.checkbox_archive');

  masterCheckbox.click(function() {
    slaveCheckboxes.prop('checked', masterCheckbox.prop('checked'));
  });

});