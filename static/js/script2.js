$(document).ready(function(){
 
  $("#btn").on('click', function(event){
    var value = $("#texto").val();
    $("#bot").append('<input type="checkbox" name="new_test_bot" id=' + value + 
        ' value=' + value +'> <label for=' + value + '>' + value + '</label>');
  
  });

});