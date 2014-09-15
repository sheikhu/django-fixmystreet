//$(document).ready(function() {
//
//     $("select[name='sel_refuse']").change(sel_refuse_handler);
//});
//
//function sel_refuse_handler(){
//
//    var textarea = $('#divRefuse textarea');
//    var select_value = $("select[name='sel_refuse']").val();
//
//    if(select_value != 'opt_refuse_0') {
//        textarea.val(sel_refuse_content[select_value]);
//    }
//
//}
//
//var sel_refuse_content = {};
//sel_refuse_content['opt_refuse_1'] = "This is a content";
//sel_refuse_content['opt_refuse_2'] = "This is another content";
//sel_refuse_content['opt_refuse_3'] = "This is a third content \n\twith carriage return and a tab";