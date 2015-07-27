$(document).ready(function() {
    var table = $('#users-table').dataTable();

    table.columnFilter({ sPlaceHolder: "head:after",
        aoColumns: [
             {type: "text"}, // name
             {type: "text"}, // phone
             {type: "text"}, // email
             {type: "select"} // roles
        ]
    });
});
