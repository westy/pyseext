from selenium.webdriver.support.ui import WebDriverWait

from pyseext.HasReferencedJavaScript import HasReferencedJavaScript
from pyseext.ComponentQuery import ComponentQuery

class GridHelper(HasReferencedJavaScript):
    """A class to help with interacting with Ext grid panels
    """
    _GET_COLUMN_HEADER_TEMPLATE = "return globalThis.PySeExt.GridHelper.getColumnHeader('{grid_cq}', '{column_text_or_dataIndex}')"

    _driver = None

    def __init__(self, driver):
        """Initialises an instance of this class

        Args:
            driver (selenium.webdriver): The webdriver to use
        """
        self._driver = driver

        # Initialise our base class
        super().__init__(driver)

    def click_column_header(self, grid_cq, column_text_or_dataIndex):
        """Clicks on the specified column header

        Args:
            grid_cq (str): The component query for the owning grid
            column_text_or_dataIndex (str): The header text or dataIndex of the grid column
        """

        # Check grid can be found and is visible
        ComponentQuery(self._driver).wait_for_single_query_visible(grid_cq);

        script = self._GET_COLUMN_HEADER_TEMPLATE.format(grid_cq=grid_cq, column_text_or_dataIndex=column_text_or_dataIndex)
        column_header = self._driver.execute_script(script)

        if column_header:
            column_header.click()
        else:
            raise GridHelper.ColumnNotFoundException(grid_cq, column_text_or_dataIndex)

    class ColumnNotFoundException(Exception):
        """Exception class thrown when we failed to find the specified column
        """

        _grid_cq = None
        _column_text_or_dataIndex = None

        def __init__(self, grid_cq, column_text_or_dataIndex, message="Failed to find column with text (or dataIndex) '{column_text_or_dataIndex}' on grid with CQ '{grid_cq}'."):
            """Initialises an instance of this exception

            Args:
                grid_cq (str): The CQ used to find the grid
                column_text_or_dataIndex (str): The header text or dataIndex of the grid column
                message (str, optional): The exception message. Defaults to "Failed to find column with text (or dataIndex) '{column_text_or_dataIndex}' on grid with CQ '{grid_cq}'.".
            """
            self.message = message
            self._grid_cq = grid_cq
            self._column_text_or_dataIndex = column_text_or_dataIndex

            super().__init__(self.message)

        def __str__(self):
            """Returns a string representation of this exception
            """
            return self.message.format(column_text_or_dataIndex=self._column_text_or_dataIndex, grid_cq=self._grid_cq)