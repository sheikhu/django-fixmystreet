// required : -http://openlayers.org/dev/OpenLayers.js
//              -http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js

if (!('fms_store' in window)) {
    window.fms_store = {};
}

/**
 * Method used to store datatable sort preferences
 */
fms_store.setTablePreferedSortedColumn = function(argSortIdx, argSortOrder) {
    if (localStorage) {
        localStorage.setItem(
            "fms-table-column-sort", 
            JSON.stringify({'idx':argSortIdx, 'order':argSortOrder/*asc or desc*/})
        );
    }
};

/**
 * Method used to store datatable invisible columns
 */
fms_store.setTableVisibleColumns = function(argUnselectedColumns) {
    if (localStorage) {
        localStorage.setItem(
            "fms-table-column-inactive", 
            JSON.stringify(argUnselectedColumns)
        );
    }
};

/**
 * Method used to get datatable sort preferences
 */
fms_store.getTablePreferedSortedColumn = function() {
    if (localStorage) {
        var sortItem = localStorage.getItem("fms-table-column-sort");
        if (sortItem) {
            return JSON.parse(sortItem);
        } else {
            return {'idx':0, 'order':'desc'};
        }
    }
};

/**
 * Method used to get datatable invisible columns
 */
fms_store.getTableInvisibleColumns = function() {
    if (localStorage) {
        var unselectedColumnsItem = localStorage.getItem("fms-table-column-inactive");
        if (unselectedColumnsItem) {
            return JSON.parse(unselectedColumnsItem);
        } else {
            return {};
        }
    }
};