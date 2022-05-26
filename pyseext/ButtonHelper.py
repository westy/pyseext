from selenium.webdriver.common.action_chains import ActionChains

from pyseext.ComponentQuery import ComponentQuery

class ButtonHelper:
    """A class to help with interacting with Ext buttons
    """

    # Class variables
    _ENABLED_BUTTON_TEMPLATE = 'button[text="{text}"][disabled=false]'
    _DISABLED_BUTTON_TEMPLATE = 'button[text="{text}"][disabled=true]'
    _MESSAGEBOX_BUTTON_TEMPLATE = 'messagebox{{isVisible(true)}} button[text="{text}"]'

    def __init__(self, driver):
        """Initialises an instance of this class

        Args:
            driver (selenium.webdriver): The webdriver to use
        """

        # Instance variables
        self._cq = ComponentQuery(driver)
        self._action_chains = ActionChains(driver)

    def click_button(self, cq, root_id=None):
        """Finds a button using the supplied component query and clicks it.

        Args:
            cq (str): The component query to find the button.
            root_id (str, optional): The id of the container within which to perform the query.
                If omitted, all components within the document are included in the search.
        """
        button = self._cq.wait_for_single_query_visible(cq, root_id)

        # Rather than call click, move mouse to button and click...
        self._action_chains.move_to_element(button)
        self._action_chains.click()
        self._action_chains.perform()

    def click_button_by_text(self, text, root_id=None):
        """Finds a visible, enabled button with the specified text and clicks it.

        Args:
            text (str): The text on the button
            root_id (str, optional): The id of the container within which to perform the query.
                If omitted, all components within the document are included in the search.
        """
        self.click_button(self._ENABLED_BUTTON_TEMPLATE.format(text=text), root_id)

    def check_button_enabled(self, text, root_id=None):
        """Checks that we can find an enabled button with the specified text.

        Args:
            text (str): The text on the button
            root_id (str, optional): The id of the container within which to perform the query.
                If omitted, all components within the document are included in the search.
        """
        self._cq.wait_for_single_query(self._ENABLED_BUTTON_TEMPLATE.format(text=text), root_id)

    def check_button_disabled(self, text, root_id=None):
        """Checks that we can find a disabled button with the specified text.

        Args:
            text (str): The text on the button
            root_id (str, optional): The id of the container within which to perform the query.
                If omitted, all components within the document are included in the search.
        """
        self._cq.wait_for_single_query(self._DISABLED_BUTTON_TEMPLATE.format(text=text), root_id)

    def click_button_on_messagebox(self, text='OK'):
        """Clicks a button on a messagebox.

        The messagebox must be visible.

        Args:
            text (str, optional): The text of the button to click. Defaults to 'OK'.
        """
        self.click_button(self._MESSAGEBOX_BUTTON_TEMPLATE.format(text=text))