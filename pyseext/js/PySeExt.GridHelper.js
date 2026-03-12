globalThis.None = null;

globalThis.PySeExt = globalThis.PySeExt || {};
globalThis.PySeExt.GridHelper = {
    /**
     * Gets the element for a column header on the specified grid, by header text or dataIndex.
     * @param {String} gridSelector The CQ for the grid
     * @param {String} columnTextOrDataIndex The text or dataIndex of the column
     * @returns {Object} The DOM node for the column header
     */
    getColumnHeader: function(gridSelector, columnTextOrDataIndex) {
        var me = this,
            columnHeader = me.__findColumnHeader(gridSelector, columnTextOrDataIndex);

        return columnHeader && columnHeader.getEl().dom;
    },

    /**
     * Gets the element for a column header's trigger on the specified grid, by header text or dataIndex.
     * @param {String} gridSelector The CQ for the grid
     * @param {String} columnTextOrDataIndex The text or dataIndex of the column
     * @returns {Object} The DOM node for the column header's trigger
     */
     getColumnHeaderTrigger: function(gridSelector, columnTextOrDataIndex) {
        var me = this,
            columnHeader = me.__findColumnHeader(gridSelector, columnTextOrDataIndex),
            columnHeaderTrigger;

        if (columnHeader) {
            columnHeaderTrigger = columnHeader.getEl().down('.x-column-header-trigger', true);
        }

        return columnHeaderTrigger;
    },

    /**
     * Clears the current selection.
     *
     * Useful if want to quickly refresh a grid without having to process all the events.
     * This will only work if the grid supports deselection.
     *
     * @param  {String}   gridSelector The selector for the grid.
     * @return {void}
     */
    clearSelection: function(gridSelector) {
        var grids = globalThis.Ext.ComponentQuery.query(gridSelector);

        if (grids && grids.length) {
            grids[0].getSelectionModel().deselectAll();
        }
    },

    /**
     * Gets the row element with the specified data or index in the grid.
     * The row is scrolled into view ready for clicking by the caller.
     *
     * The grid must be visible.
     *
     * @param  {String}        gridSelector The selector for the grid.
     * @param  {Object|Number} rowData      The index of or an object containing the row data for the record to be found.
     * @return {Element} The element for the found row.
     */
    getRow: function(gridSelector, rowData) {
        var me = this,
            grids = globalThis.Ext.ComponentQuery.query(gridSelector),
            grid,
            store,
            rowIndex;

        if (grids && grids.length) {
            grid = grids[0];
            store = grid.getStore();

            rowIndex = me.__findRowIndex(rowData, store);

            if (rowIndex !== -1) {
                return grid.getView().getRow(rowIndex);
            }
        }
        
        return null;
    },

    /**
     * Gets the row data with the specified data or index in the grid.
     * The row is scrolled into view ready for clicking by the caller.
     *
     * The grid must be visible.
     *
     * @param  {String} gridSelector   The selector for the grid.
     * @param  {Object|Number} rowData The index of or an object containing the row data for the record to be found.
     * @return {Object[]} The data for the found row.
     */
    getRowData: function(gridSelector, rowData) {
        var me = this,
            grids = globalThis.Ext.ComponentQuery.query(gridSelector),
            grid,
            store,
            rowIndex;

        if (grids && grids.length) {
            grid = grids[0];
            store = grid.getStore();

            rowIndex = me.__findRowIndex(rowData, store);

            if (rowIndex !== -1) {
                var data = store.getAt(rowIndex).getData();
                var converted = {};
                Object.keys(data).forEach(function (key) {
                    var value = data[key];
                    if (value instanceof Date) {
                        // Convert to ISO 8601 string, which Python can parse easily
                        converted[key] = value.toLocaleString("en-GB", { timeZone: "Europe/London" });
                    } else {
                        converted[key] = value;
                    }
                });

                return converted;
            }
        }

        return null;
    },

    /**
     * Trims the specified row data to contain just the required fields.
     *
     * Useful when we have stored some row data, and want to select it again later, but some of the ids of times
     * may be different.
     *
     * @param  {Object} rowData        The row data to trim.
     * @param  {Array}  requiredFields An array of string indicating the fields that are required from the row data.
     * @return {Object} A copy of the row data object, with only the required fields included.
     */
    __trimRowData: function(rowData, requiredFields) {
        var trimmedRowData = {},
            i;

        for (i = 0; i < requiredFields.length; i += 1) {
            trimmedRowData[requiredFields[i]] = rowData[requiredFields[i]];
        }

        return trimmedRowData;
    },

    /**
     * Retrieves the selection of the specified grid.
     * @private
     * @param  {String}         gridSelector       The selector for the grid.
     * @param  {Function}       callback           The function to call when the done.
     * @param  {Array}          callback.selection The grids current selection.
     * @return {void}
     */
    __getSelection: function(gridSelector, callback) {
        var grids = globalThis.Ext.ComponentQuery.query(gridSelector);

        if (grids && grids.length) {
            globalThis.Ext.callback(callback, this, [grids[0].getSelectionModel().getSelection()]);
        }
    },

    /**
     * Finds on a column header on a grid.
     * @private
     * @param  {String} gridSelector          The selector for the grid.
     * @param  {String} columnTextOrDataIndex The text or dataIndex of the column to find.
     * @return {Ext.Component}                The column header component
     */
     __findColumnHeader: function(gridSelector, columnTextOrDataIndex) {
        var me = this,
            grid,
            dataColumns,
            i,
            dataColumn,
            columnHeader;

        components = Ext.ComponentQuery.query(gridSelector);
        if (components && components.length) {
            grid = components[0];

            dataColumns = grid.headerCt.gridDataColumns

            // Find column header
            for (i = 0; i < dataColumns.length; i += 1) {
                dataColumn = dataColumns[i];

                if ((dataColumn.dataIndex === columnTextOrDataIndex) ||
                    (dataColumn.text === columnTextOrDataIndex)) {

                    columnHeader = dataColumn;
                    break;
                }
            }
        }

        return columnHeader;
    },

    /**
     * Gets the row index with the specified data or index in the grid.
     * The row is scrolled into view ready for clicking by the caller.
     *
     * The grid must be visible.
     *
     * @param  {Object|Number} rowData The index of or an object containing the row data for the record to be found.
     * @return {Number} The index for the row record, or -1 if not found
     */
    __findRowIndex: function(rowData, store) {
        var rowIndex = -1,
            foundIndex,
            prop;

        if (typeof(rowData) === 'number') {
            foundIndex = rowData;

            // Verify it's not bollocks
            if (!Ext.isNumber(parseInt(foundIndex)) || foundIndex < 0) {
                globalThis.Ext.raise('If attempting to get a row for a specific index, the index must be an integer greater than or equal to zero.');
            }

            // Check that found index is within bounds, if so grab the row.
            if (foundIndex < store.getCount()) {
                rowIndex = foundIndex;
            }
        } else {
            foundIndex = store.findBy(function(record, id) {
                var hasRecordBeenFound = true;

                for (prop in rowData) {
                    if (rowData.hasOwnProperty(prop)) {
                        if (record.get(prop) !== rowData[prop]) {
                            hasRecordBeenFound = false;
                            break;
                        }
                    }
                }

                return hasRecordBeenFound;
            });

            // This could be -1, but that's fine since that's the expected "not found" result.
            rowIndex = foundIndex;
        }

        return rowIndex;
    }
};
