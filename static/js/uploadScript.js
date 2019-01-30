$(document).ready(function(){
   $('#upload-filter-button').hide();
   $('#upload_selects').bind('change',function(){
       var value = $(this).val();
       if (value == "答案相似度"){
           $('#upload-filter-button').show();
       } else {
           $('#upload-filter-button').hide();
       }
   })
});