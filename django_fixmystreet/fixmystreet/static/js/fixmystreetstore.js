// required : -http://openlayers.org/dev/OpenLayers.js
//              -http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js

if (!('fms_store' in window)) {
    window.fms_store = {};
    window.fms_store.KEY_PREFERRED_DATA_TABLE_COLUMN_SORT = "fms-table-column-sort";
    window.fms_store.KEY_DATA_TABLE_INACTIVE_COLUMN = "fms-table-column-inactive";
    window.fms_store.KEY_DATA_TABLE_MAX_ROWS = "fms-table-max-rows";
}

/**
 * Method used to store datatable sort preferences
 */
fms_store.setTablePreferedSortedColumn = function(argSortIdx, argSortOrder) {
    if (localStorage) {
        localStorage.setItem(
            this.KEY_PREFERRED_DATA_TABLE_COLUMN_SORT,
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
            this.KEY_DATA_TABLE_INACTIVE_COLUMN,
            JSON.stringify(argUnselectedColumns)
        );
    }
};

/**
 * Method used to get datatable sort preferences
 */
fms_store.getTablePreferedSortedColumn = function() {
    if (localStorage) {
        var sortItem = localStorage.getItem(this.KEY_PREFERRED_DATA_TABLE_COLUMN_SORT);
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
        var unselectedColumnsItem = localStorage.getItem(this.KEY_DATA_TABLE_INACTIVE_COLUMN);
        if (unselectedColumnsItem) {
            return JSON.parse(unselectedColumnsItem);
        } else {
            return {};
        }
    }
};

/**
 * Method used to store datatable max number of records in the result set
 */
fms_store.setTableMaxRows = function(argMaxRows) {
    if (localStorage) {
        localStorage.setItem(this.KEY_DATA_TABLE_MAX_ROWS, argMaxRows);
    }
};

/**
 * Method used to get datatable max number of records in the result set
 */
fms_store.getTableMaxRows = function(argMaxRows) {
    if (localStorage) {
        return localStorage.getItem(this.KEY_DATA_TABLE_MAX_ROWS) || argMaxRows;
    }
    return argMaxRows;
};
