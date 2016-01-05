$(document).ready(function() {

     $("select[name='sel_refuse']").change(sel_refuse_handler);
});

function sel_refuse_handler(){

    var textarea = $('#divRefuse textarea');
    var select_value = $("select[name='sel_refuse']").val();

    if(select_value != 'opt_refuse_0') {
        textarea.val(sel_refuse_content[select_value]);
    }

}

var sel_refuse_content = {};
sel_refuse_content['opt_refuse_1'] = gettext("L'incident que vous avez signalé n’est pas assez clairement décrit. Nous vous demandons d’expliquer le problème de la manière la plus précise possible, de préférence avec une ou plusieurs photos du problème et de l’endroit où il se trouve.");
sel_refuse_content['opt_refuse_2'] = gettext("L'incident que vous avez signalé ne rentre dans le domaine d’application  de Fix My Street.");
sel_refuse_content['opt_refuse_3'] = gettext("L'incident que vous avez signalé se trouve à un endroit qui fait partie d’un projet de réaménagement et sera restauré durant la mise en œuvre du projet.");
sel_refuse_content['opt_refuse_4'] = gettext("L'incident que vous avez signalé est sur une propriété privée et n'est pas la responsabilité de Fix My Street.");
sel_refuse_content['opt_refuse_5'] = gettext("Cet incident a déjà été signalé et est en attente de traitement.");
sel_refuse_content['opt_refuse_6'] = gettext("Not for Sibelga eclairage");
