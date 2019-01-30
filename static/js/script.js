$(document).ready(function(){
  var open = true;
  var check = false;
  $('.textanim-hidden').show()

  $('.table-add').click(function(){
    $('.dispatch_input_row:first').clone().insertAfter('.dispatch_input_row:last');
  });

  $('.show').on('click', function(event){
    if(open){
      open = false;
      
      $(this).next(".textanim-hidden").stop().slideToggle(300);
    }
    else{
      open = true;
      $('.textanim-hidden').show()
    }
  });
  $(".query-answer-page").hide();
  $(".query-answer-page").slideDown(500); 
   var now = new Date();
 
  var day = ("0" + now.getDate()).slice(-2);
  var month = ("0" + (now.getMonth() + 1)).slice(-2);

  var today = now.getFullYear()+"-"+(month)+"-"+(day) ;


   $('#date').val(today);
  $("#submit_annotation").click(function(e){
    if($(".checkbox-button-input:checked").length == 0){
      e.preventDefault();
      alert("You must check one checkbox!");
    }
  });
});

