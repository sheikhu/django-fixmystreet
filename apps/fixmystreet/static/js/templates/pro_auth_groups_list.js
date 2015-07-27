$(document).ready(function() {
    var table = $('#groups-table').dataTable();

    table.columnFilter({ sPlaceHolder: "head:after",
        aoColumns: [
             {type: "text"}, // name
             {type: "text"}, // phone
             {type: "text"} // email
        ]
    });
});
