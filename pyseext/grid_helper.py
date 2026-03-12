"""
Module that contains our GridHelper class.
"""

import logging
import random
from typing import List, Union

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By

from pyseext.has_referenced_javascript import HasReferencedJavaScript
from pyseext.component_query import ComponentQuery
from pyseext.input_helper import InputHelper
from pyseext.menu_helper import MenuHelper
from pyseext.store_helper import StoreHelper
from pyseext.core import Core


class GridHelper(HasReferencedJavaScript):
    """A class to help with interacting with Ext grid panels"""

    # Public class properties
    GRID_CQ: str = "gridpanel"
    """The component query to use to find a grid panel"""

    # Private class variables
    _GET_COLUMN_HEADER_TEMPLATE: str = (
        "return globalThis.PySeExt.GridHelper.getColumnHeader('{grid_cq}', '{column_text_or_data_index}')"
    )
    """The script template to use to call the JavaScript method PySeExt.GridHelper.getColumnHeader
    Requires the inserts: {grid_cq}, {column_text_or_data_index}"""

    _GET_COLUMN_HEADER_TRIGGER_TEMPLATE: str = (
        "return globalThis.PySeExt.GridHelper.getColumnHeaderTrigger('{grid_cq}', '{column_text_or_data_index}')"
    )
    """The script template to use to call the JavaScript method PySeExt.GridHelper.getColumnHeaderTrigger
    Requires the inserts: {grid_cq}, {column_text_or_data_index}"""

    _CLEAR_SELECTION_TEMPLATE: str = (
        "return globalThis.PySeExt.GridHelper.clearSelection('{grid_cq}')"
    )
    """The script template to use to call the JavaScript method PySeExt.GridHelper.clearSelection
    Requires the inserts: {grid_cq}"""

    _GET_ROW_TEMPLATE: str = (
        "return globalThis.PySeExt.GridHelper.getRow('{grid_cq}', {row_data})"
    )
    """The script template to use to call the JavaScript method PySeExt.GridHelper.getRow
    Requires the inserts: {grid_cq}, {row_data}"""

    _GET_ROW_DATA_TEMPLATE: str = (
        "return globalThis.PySeExt.GridHelper.getRowData('{grid_cq}', {row_data})"
    )
    """The script template to use to call the JavaScript method PySeExt.GridHelper.getRow
    Requires the inserts: {grid_cq}, {row_data}"""

    def __init__(self, driver: WebDriver):
        """Initialises an instance of this class

        Args:
            driver (WebDriver): The webdriver to use
        """

        # Instance variables
        self._logger = logging.getLogger(__name__)
        """The Logger instance for this class instance"""

        self._driver = driver
        """The WebDriver instance for this class instance"""

        self._cq = ComponentQuery(driver)
        """The `ComponentQuery` instance for this class instance"""

        self._input_helper = InputHelper(driver)
        """The `InputHelper` instance for this class instance"""

        self._menu_helper = MenuHelper(driver)
        """The `MenuHelper` instance for this class instance"""

        self._store_helper = StoreHelper(driver)
        """The `StoreHelper` instance for this class instance"""

        self._action_chains = ActionChains(driver)
        """The ActionChains instance for this class instance"""

        self._core = Core(driver)

        # Initialise our base class
        super().__init__(driver, self._logger)

    def get_column_header(
        self, grid_cq: str, column_text_or_data_index: str
    ) -> WebElement:
        """Gets the element for the specified column header

        Args:
            grid_cq (str): The component query for the owning grid
            column_text_or_data_index (str): The header text or dataIndex of the grid column

        Returns:
            WebElement: The DOM element for the column header
        """

        # Check grid can be found and is visible
        self._cq.wait_for_single_query_visible(grid_cq)

        script = self._GET_COLUMN_HEADER_TEMPLATE.format(
            grid_cq=grid_cq, column_text_or_data_index=column_text_or_data_index
        )
        self.ensure_javascript_loaded()
        column_header = self._driver.execute_script(script)

        if column_header:
            return column_header

        raise GridHelper.ColumnNotFoundException(grid_cq, column_text_or_data_index)

    def is_column_visible(self, grid_cq: str, column_text_or_data_index: str) -> bool:
        """Determines whether the specified column is visible,
        Throws a ColumnNotFoundException if the column does not exist.

        Args:
            grid_cq (str): The component query for the owning grid
            column_text_or_data_index (str): The header text or dataIndex of the grid column

        Returns:
            True if the column is visible, False otherwise.
        """
        return self.get_column_header(grid_cq, column_text_or_data_index).is_displayed()

    def is_column_hidden(self, grid_cq: str, column_text_or_data_index: str) -> bool:
        """Determines whether the specified column is hidden.
        Throws a ColumnNotFoundException if the column does not exist.

        Args:
            grid_cq (str): The component query for the owning grid
            column_text_or_data_index (str): The header text or dataIndex of the grid column

        Returns:
            True if the column is hidden, False otherwise.
        """
        return not self.get_column_header(
            grid_cq, column_text_or_data_index
        ).is_displayed()

    def check_columns_are_visible(
        self, grid_cq: str, column_text_or_data_indexes: list[str]
    ) -> list[WebElement]:
        """Checks that the specified columns are all visible on the specified grid.
        Throws a ColumnNotFoundException if the column does not exist.

        Args:
            grid_cq (str): The component query for the owning grid
            column_text_or_data_indexes (list[str]): An array containing the header text or dataIndex of the grid columns to check

        Returns:
            An array of columns that are not visible, if any.
        """
        columns_not_visible = []

        for column_text_or_data_index in column_text_or_data_indexes:
            is_visible = self.is_column_visible(grid_cq, column_text_or_data_index)
            if not is_visible:
                columns_not_visible.append(column_text_or_data_index)

        return columns_not_visible

    def check_columns_are_hidden(
        self, grid_cq: str, column_texts_or_data_indexes: list[str]
    ) -> list[WebElement]:
        """Checks that the specified columns are all hidden on the specified grid.
        Throws a ColumnNotFoundException if the column does not exist.

        Args:
            grid_cq (str): The component query for the owning grid
            column_texts_or_data_indexes (list[str]): An array containing the header text or dataIndex of the grid columns to check

        Returns:
            An array of columns that are not hidden, if any.
        """
        column_not_hidden = []

        for column_text_or_data_index in column_texts_or_data_indexes:
            is_hidden = self.is_column_hidden(grid_cq, column_text_or_data_index)
            if not is_hidden:
                column_not_hidden.append(column_text_or_data_index)

        return column_not_hidden

    def click_column_header(self, grid_cq: str, column_text_or_data_index: str):
        """Clicks on the specified column header.
        The column must be visible.

        Args:
            grid_cq (str): The component query for the owning grid
            column_text_or_data_index (str): The header text or dataIndex of the grid column
        """
        column_header = self.get_column_header(grid_cq, column_text_or_data_index)

        self._logger.info(
            "Clicking column header '%s' on grid with CQ '%s'",
            column_text_or_data_index,
            grid_cq,
        )

        self._action_chains.move_to_element(column_header)
        self._action_chains.click()
        self._action_chains.perform()

    def get_column_header_trigger(
        self, grid_cq: str, column_text_or_data_index: str
    ) -> WebElement:
        """Gets the element for the specified column header's trigger

        Args:
            grid_cq (str): The component query for the owning grid
            column_text_or_data_index (str): The header text or dataIndex of the grid column

        Returns:
            WebElement: The DOM element for the column header trigger.
        """

        # Check grid can be found and is visible
        self._cq.wait_for_single_query_visible(grid_cq)

        script = self._GET_COLUMN_HEADER_TRIGGER_TEMPLATE.format(
            grid_cq=grid_cq, column_text_or_data_index=column_text_or_data_index
        )
        self.ensure_javascript_loaded()
        column_header_trigger = self._driver.execute_script(script)

        if column_header_trigger:
            return column_header_trigger

        raise GridHelper.ColumnNotFoundException(grid_cq, column_text_or_data_index)

    def click_column_header_trigger(self, grid_cq: str, column_text_or_data_index: str):
        """Clicks on the specified column header's trigger

        Args:
            grid_cq (str): The component query for the owning grid
            column_text_or_data_index (str): The header text or dataIndex of the grid column
        """
        # We need to move to the header before the trigger becomes interactable
        column_header = self.get_column_header(grid_cq, column_text_or_data_index)
        self._action_chains.move_to_element(column_header).perform()

        column_header_trigger = self.get_column_header_trigger(
            grid_cq, column_text_or_data_index
        )

        self._logger.info(
            "Clicking column header trigger '%s' on grid with CQ '%s'",
            column_text_or_data_index,
            grid_cq,
        )

        self._action_chains.move_to_element(column_header_trigger)
        self._action_chains.click()
        self._action_chains.perform()

    def filter_string_column(
        self,
        grid_cq: str,
        column_text_or_data_index: str,
        filter_value: str,
        wait_for_store_loaded: bool = True,
        clear_first: bool = False,
    ):
        """Filters a string column on a grid for the specified value.

        Args:
            grid_cq (str): The component query for the owning grid.
            column_text_or_data_index (str): The header text or dataIndex of the grid column.
            filter_value (str): The value to filter the column by.
            wait_for_store_loaded (bool, optional): Indicates whether to wait for the store to load. Defaults to True.
            clear_first (bool, optional): Indicates whether to clear the filter element first. Defaults to False.
        """
        self.click_column_header_trigger(grid_cq, column_text_or_data_index)
        self._menu_helper.move_to_menu_item_by_text("Filters")

        filter_textbox = self._cq.wait_for_single_query_visible(
            'textfield[emptyText="Enter Filter Text..."]'
        )

        if wait_for_store_loaded:
            self._store_helper.reset_store_load_count(grid_cq)

        self._input_helper.type_into_element(
            filter_textbox, filter_value, clear_first=clear_first
        )

        if wait_for_store_loaded:
            self._store_helper.wait_for_store_loaded(grid_cq)

        # Close filter and then column menu
        self._input_helper.type_escape()
        self._input_helper.type_escape()
        self._core.wait_for_no_ajax_requests_in_progress()

    def filter_list_column(
        self,
        grid_cq: str,
        column_text_or_data_index: str,
        filter_values_to_toggle: list[str],
        wait_for_store_loaded: bool = True,
    ):
        """Toggles the values on a list filtered column on a grid.

        Args:
            grid_cq (str): The component query for the owning grid.
            column_text_or_data_index (str): The header text or dataIndex of the grid column.
            filter_values_to_toggle (list[str]): The filter values to toggle.
            wait_for_store_loaded (bool, optional): Indicates whether to wait for the store to load. Defaults to True.
        """
        self.click_column_header_trigger(grid_cq, column_text_or_data_index)
        self._menu_helper.move_to_menu_item_by_text("Filters")

        if wait_for_store_loaded:
            self._store_helper.reset_store_load_count(grid_cq)

        for filter_value_to_toggle in filter_values_to_toggle:
            self._menu_helper.click_menu_item_by_text(filter_value_to_toggle)

        if wait_for_store_loaded:
            self._store_helper.wait_for_store_loaded(grid_cq)

        # Close filter and then column menu
        self._input_helper.type_escape()
        self._input_helper.type_escape()

    def filter_number_column(
        self,
        grid_cq: str,
        column_text_or_data_index: str,
        equal_to: Union[None, float] = None,
        less_than: Union[None, float] = None,
        greater_than: Union[None, float] = None,
        wait_for_store_loaded: bool = True,
    ):
        """Filters a number column on a grid for the specified values.

        Args:
            grid_cq (str): The component query for the owning grid.
            column_text_or_data_index (str): The header text or dataIndex of the grid column.
            filter_values_to_toggle (list[str]): The filter values to toggle.
            wait_for_store_loaded (bool, optional): Indicates whether to wait for the store to load. Defaults to True.
        """
        self.click_column_header_trigger(grid_cq, column_text_or_data_index)
        self._menu_helper.move_to_menu_item_by_text("Filters")

        if wait_for_store_loaded:
            self._store_helper.reset_store_load_count(grid_cq)

        filter_textboxes = self._cq.wait_for_query(
            'textfield[emptyText="Enter Number..."]'
        )

        # clear_first does not work with these :/
        # Double-clicking then either typing or deleting should do it.
        self._action_chains.move_to_element(filter_textboxes[0])
        self._action_chains.double_click()
        self._action_chains.perform()

        if less_than is not None:
            self._input_helper.type_into_element(
                filter_textboxes[0], less_than, clear_first=False
            )
        else:
            self._input_helper.type_delete()

        self._action_chains.move_to_element(filter_textboxes[1])
        self._action_chains.double_click()
        self._action_chains.perform()

        if greater_than is not None:
            self._input_helper.type_into_element(
                filter_textboxes[1], greater_than, clear_first=False
            )
        else:
            self._input_helper.type_delete()

        self._action_chains.move_to_element(filter_textboxes[2])
        self._action_chains.double_click()
        self._action_chains.perform()

        if equal_to is not None:
            self._input_helper.type_into_element(
                filter_textboxes[2], equal_to, clear_first=False
            )
        else:
            self._input_helper.type_delete()

        if wait_for_store_loaded:
            self._store_helper.wait_for_store_loaded(grid_cq)

        # Close filter and then column menu
        self._input_helper.type_escape()
        self._input_helper.type_escape()

    def toggle_column_filter(
        self,
        grid_cq: str,
        column_text_or_data_index: str,
        wait_for_store_loaded: bool = True,
    ):
        """Toggles the filter on a column by clicking on the filters element.

        Args:
            grid_cq (str): The component query for the owning grid.
            column_text_or_data_index (str): The header text or dataIndex of the grid column.
            wait_for_store_loaded (bool, optional): Indicates whether to wait for the store to load. Defaults to True.
        """
        self.click_column_header_trigger(grid_cq, column_text_or_data_index)
        filter_menu_item = self._menu_helper.try_get_menu_item_by_text("Filters")

        if wait_for_store_loaded:
            self._store_helper.reset_store_load_count(grid_cq)

        self._action_chains.move_to_element(filter_menu_item)
        self._action_chains.click()
        self._action_chains.perform()

        if wait_for_store_loaded:
            self._store_helper.wait_for_store_loaded(grid_cq)

        # Close filter and then column menu
        self._input_helper.type_escape()
        self._input_helper.type_escape()

    def clear_selection(self, grid_cq: str):
        """Clears the current selection.

        Useful if want to quickly refresh a grid without having to process all the events.
        This will only work if the grid supports deselection.

        Args:
            grid_cq (str): The component query for the grid
        """
        # Check grid can be found and is visible
        self._cq.wait_for_single_query_visible(grid_cq)

        self._logger.info("Clearing selection on grid with CQ '%s'", grid_cq)

        script = self._CLEAR_SELECTION_TEMPLATE.format(grid_cq=grid_cq)
        self.ensure_javascript_loaded()
        self._driver.execute_script(script)

    def get_row(
        self,
        grid_cq: str,
        row_data: Union[int, dict],
        should_throw_exception: bool = True,
    ) -> WebElement:
        """Gets the element for the row with the specified data or index in the grid.

        The grid must be visible.

        Args:
            grid_cq (str): The component query for the grid
            row_data (Union[int, dict]): The row data or index for the record to be found.
            should_throw_exception (bool): Indicates whether this method should throw an exception
                                           if the row is not found. Defaults to True.

        Returns:
            WebElement: The DOM element for the row or None if not found (and not thrown)
        """
        # Check grid can be found and is visible
        self._cq.wait_for_single_query_visible(grid_cq)

        script = self._GET_ROW_TEMPLATE.format(grid_cq=grid_cq, row_data=row_data)
        self.ensure_javascript_loaded()
        row = self._driver.execute_script(script)

        if row or not should_throw_exception:
            return row

        raise GridHelper.RowNotFoundException(grid_cq, row_data)

    def get_row_data(
        self,
        grid_cq: str,
        row_data: Union[int, dict],
        should_throw_exception: bool = True,
    ) -> dict:
        """Gets the data for the row with the specified data or index in the grid.

        The grid must be visible.

        Args:
            grid_cq (str): The component query for the grid
            row_data (Union[int, dict]): The row data or index for the record to be found.
            should_throw_exception (bool): Indicates whether this method should throw an exception
                                           if the row is not found. Defaults to True.

        Returns:
            Dict: Dict containing the store for the row or None if not found (and not thrown)
        """
        # Check grid can be found and is visible
        self._cq.wait_for_single_query_visible(grid_cq)

        script = self._GET_ROW_DATA_TEMPLATE.format(grid_cq=grid_cq, row_data=row_data)
        self.ensure_javascript_loaded()
        row = self._driver.execute_script(script)

        if row or not should_throw_exception:
            return row

        raise GridHelper.RowNotFoundException(grid_cq, row_data)

    def click_row(self, grid_cq: str, row_data: Union[int, dict]):
        """Clicks the row with the specified data or index in the grid.

        The grid must be visible.

        Args:
            grid_cq (str): The component query for the grid
            row_data (Union[int, dict]): The row data or index for the record to be found and clicked.
        """
        try:
            # Check grid can be found and is visible
            row = self.get_row(grid_cq, row_data)

            self._logger.info(
                "Clicking clicking row '%s' on grid with CQ '%s'", row_data, grid_cq
            )

            self._action_chains.move_to_element(row)
            self._action_chains.click()
            self._action_chains.perform()
            self.check_row_selected(grid_cq, row_data)

        except StaleElementReferenceException:

            row = self.get_row(grid_cq, row_data)

            self._action_chains.move_to_element(row)
            self._action_chains.click()
            self._action_chains.perform()
            self.check_row_selected(grid_cq, row_data)

    def wait_for_row(
        self, grid_cq: str, row_data: Union[int, dict], timeout: float = 60
    ) -> WebElement:
        """Waits for the specified row to appear in the grid, reloading the store until
        it is found, or until the timeout is hit.

        Args:
            grid_cq (str): The component query for the grid.
            row_data (Union[int, dict]): The row data or index of the record we are waiting for.
            timeout (int, optional): The number of seconds to wait for the row before erroring. Defaults to 60.

        Returns:
            WebElement: The DOM element for the row
        """
        WebDriverWait(self._driver, timeout).until(
            GridHelper.RowFoundExpectation(grid_cq, row_data)
        )
        return self.get_row(grid_cq, row_data)

    def wait_to_click_row(
        self, grid_cq: str, row_data: Union[int, dict], timeout: float = 120
    ):
        """Waits for the specified row to appear in the grid, reloading the store until
        it is found, or until the timeout is hit.
        Once we have found the row it is clicked.

        Args:
            grid_cq (str): The component query for the grid.
            row_data (Union[int, dict]): The row data or index of the record we are waiting for.
            timeout (int, optional): The number of seconds to wait for the row before erroring. Defaults to 60.
        """
        WebDriverWait(self._driver, timeout).until(
            GridHelper.RowFoundExpectation(grid_cq, row_data)
        )
        self._core.wait_for_no_ajax_requests_in_progress()
        self.click_row(grid_cq, row_data)
        self.check_row_selected(grid_cq, row_data)

    def wait_and_click_multiple_rows(
            self, grid_cq: str, row_data: List[Union[int, dict]]
    ):
        """Waits for the specified row to appear in the grid, reloading the store until
        it is found, or until the timeout is hit.
        Once we have found the row it is clicked and holds CONTROL and clicks on other given row. This mimics the action of selecting 
        multiple rows

        Args:
            grid_cq (str): The component query for the grid.
            row_data (List[Union[int, dict]]): The row data or index of the record we are waiting for to be clicked after holding CONTROL.
        """
        if not row_data:
            raise ValueError("row_data must contain at least one row")
        self.wait_to_click_row(grid_cq, row_data[0])
        for row in row_data[1:]:
            row_data_found = self.get_row(grid_cq, row)
            self._action_chains.key_down(Keys.CONTROL).click(row_data_found).key_up(Keys.CONTROL).perform()

    def toggle_columns(
        self, grid_cq: str, column_text_or_data_index: str, columns_to_toggle: list[str]
    ):
        """Toggles a list of columns on the specified grid.
        Any that are visible will be hidden, and any that a currently hidden will be shown.

        Args:
            grid_cq (str): The component query for the owning grid.
            column_text_or_data_index (str): The header text or dataIndex of the grid column to use for the interaction.
            columns_to_toggle (list[str]): The list of columns to toggle.
        """

        # Use first visible column for our interaction
        self.click_column_header_trigger(grid_cq, column_text_or_data_index)

        # Get the 'Columns' menu itema and move to it, so that submenu shows.
        filter_menu_item = self._menu_helper.try_get_menu_item_by_text("Columns")
        self._action_chains.move_to_element(filter_menu_item)
        self._action_chains.perform()

        for column in columns_to_toggle:
            column_to_click = self._cq.wait_for_single_query_visible(
                f'menucheckitem[text="{column}"]'
            )

            self._action_chains.move_to_element(column_to_click)
            self._action_chains.pause(
                random.uniform(
                    self._input_helper.INPUT_SLEEP_MINIMUM,
                    self._input_helper.INPUT_SLEEP_MAXIMUM,
                )
            )
            self._action_chains.click()
            self._action_chains.pause(
                random.uniform(
                    self._input_helper.INPUT_SLEEP_MINIMUM,
                    self._input_helper.INPUT_SLEEP_MAXIMUM,
                )
            )
            self._action_chains.perform()

        # Close columns submenu, and grid menu.
        self._input_helper.type_escape()
        self._input_helper.type_escape()

    def check_row_selected(self, grid_cq: str, row_data: Union[int, dict]):
        """ Checks whether a row is currently selected. If false then the row is clicked.

        Args:
            grid_cq (str): CQ of grid
            row_data (Union[int, dict]): Data of row to check.
        """
        check_row = self.get_row(
            grid_cq,
            row_data,
        )

        #Need to go up to table level from row
        table = check_row.find_element(By.XPATH, "../..")
        current_classes = "x-grid-item-selected" in table.get_attribute("class")
        if current_classes:
            return
        else:
            self.wait_to_click_row(grid_cq, row_data)


    class ColumnNotFoundException(Exception):
        """Exception class thrown when we failed to find the specified column"""

        def __init__(
            self,
            grid_cq: str,
            column_text_or_data_index: str,
            message: str = "Failed to find column with text (or dataIndex) '{column_text_or_data_index}' on grid with CQ '{grid_cq}'.",
        ):
            """Initialises an instance of this exception

            Args:
                grid_cq (str): The CQ used to find the grid
                column_text_or_data_index (str): The header text or dataIndex of the grid column
                message (str, optional): The exception message. Defaults to "Failed to find column with text (or dataIndex) '{column_text_or_data_index}' on grid with CQ '{grid_cq}'.".
            """
            self.message = message
            self._grid_cq = grid_cq
            self._column_text_or_data_index = column_text_or_data_index

            super().__init__(self.message)

        def __str__(self):
            """Returns a string representation of this exception"""
            return self.message.format(
                column_text_or_data_index=self._column_text_or_data_index,
                grid_cq=self._grid_cq,
            )

    class RowNotFoundException(Exception):
        """Exception class thrown when we failed to find the specified row"""

        def __init__(
            self,
            grid_cq: str,
            row_data: Union[int, dict],
            message: str = "Failed to find row with data (or index) '{row_data}' on grid with CQ '{grid_cq}'.",
        ):
            """Initialises an instance of this exception

            Args:
                grid_cq (str): The CQ used to find the grid
                row_data (Union[int, dict]): The row data or index for the record
                message (str, optional): The exception message. Defaults to "Failed to find row with data (or index) '{row_data}' on grid with CQ '{grid_cq}'.".
            """
            self.message = message
            self._grid_cq = grid_cq
            self._row_data = row_data

            super().__init__(self.message)

        def __str__(self):
            """Returns a string representation of this exception"""
            return self.message.format(row_data=self._row_data, grid_cq=self._grid_cq)

    class RowFoundExpectation:
        """An expectation for checking that a row has been found"""

        def __init__(self, grid_cq: str, row_data: Union[int, dict]):
            """Initialises an instance of this class.

            Args:
                grid_cq (str): The component query for the grid.
                row_data (Union[int, dict]): The row data or index of the record we are waiting for.
            """
            self._grid_cq = grid_cq
            self._row_data = row_data

        def __call__(self, driver):
            """Method that determines whether a row was found.

            If the row is not found the grid is refreshed and the load waited for.
            """
            grid_helper = GridHelper(driver)

            row = grid_helper.get_row(self._grid_cq, self._row_data, False)
            if row:
                return True

            # Trigger a reload, and wait for it to complete
            store_helper = StoreHelper(driver)
            store_helper.reset_store_load_count(self._grid_cq)
            store_helper.trigger_reload(self._grid_cq)
            store_helper.wait_for_store_loaded(self._grid_cq)
            return False
