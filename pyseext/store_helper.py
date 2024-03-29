"""
Module that contains our StoreHelper class.
"""
import logging

from selenium.webdriver.remote.webdriver import WebDriver

from pyseext.has_referenced_javascript import HasReferencedJavaScript

class StoreHelper(HasReferencedJavaScript):
    """A class to help with using stores, through Ext's interfaces."""

    # Class variables
    _RESET_STORE_LOAD_COUNT_TEMPLATE: str = "return globalThis.PySeExt.StoreHelper.resetStoreLoadCount('{store_holder_cq}')"
    """The script template to use to call the JavaScript method PySeExt.StoreHelper.resetStoreLoadCount
    Requires the inserts: {store_holder_cq}"""

    _WAIT_FOR_STORE_LOADED_TEMPLATE: str = "return globalThis.PySeExt.StoreHelper.waitForStoreLoaded('{store_holder_cq}', callback)"
    """The script template to use to call the asynchronous JavaScript method PySeExt.StoreHelper.waitForStoreLoaded
    Requires the inserts: {store_holder_cq}

    Use our base classes `get_async_script_content` method call it."""

    _RELOAD_STORE_TEMPLATE: str = "return globalThis.PySeExt.StoreHelper.reload('{store_holder_cq}')"
    """The script template to use to call the JavaScript method PySeExt.StoreHelper.reload
    Requires the inserts: {store_holder_cq}"""

    _CHECK_STORE_CONTAINS_TEMPLATE: str = "return globalThis.PySeExt.StoreHelper.checkStoreContains('{store_holder_cq}', {data}, {should_only_contain_specified_data})"
    """The script template to use to call the JavaScript method PySeExt.StoreHelper.checkStoreContains
    Requires the inserts: {store_holder_cq}, {data}, {should_only_contain_specified_data}"""

    def __init__(self, driver: WebDriver):
        """Initialises an instance of this class

        Args:
            driver (WebDriver): The webdriver to use
        """
        self._logger = logging.getLogger(__name__)
        """The Logger instance for this class instance"""

        self._driver = driver
        """The WebDriver instance for this class instance"""

        # Initialise our base class
        super().__init__(driver, self._logger)

    def reset_store_load_count(self, store_holder_cq: str):
        """Resets the load count on the specified store, provided the store is not configured with autoLoad set to true.

        If set to auto load then this method does nothing.

        The load count on a store is incremented everytime a load occurs. It is not reset when the data is cleared.
        A store's isLoaded method returns true if the load count is greater than zero.

        Calling this method is useful to use before performing an action that will trigger a load, since you can then
        wait for the stores isLoaded method to return true.
        This is far more reliable than waiting for the load event, since it may have already been fired by the time the
        test gets that far.

        Args:
            store_holder_cq (str): The component query to use to find the store holder.
        """
        self._logger.debug("Resetting loadCount on store owned by '%s'", store_holder_cq)

        script = self._RESET_STORE_LOAD_COUNT_TEMPLATE.format(store_holder_cq=store_holder_cq)
        self.ensure_javascript_loaded()
        self._driver.execute_script(script)

    def wait_for_store_loaded(self, store_holder_cq: str):
        """ Waits for the specified store to return true from its isLoaded method.

        Should generally be used after calling #resetStoreLoadCount and performing an
        action that triggers a store load.

        Args:
            store_holder_cq (str): The component query to use to find the store holder.
        """
        self._logger.debug("Waiting for store owned by '%s' to load", store_holder_cq)

        async_script = self.get_async_script_content(self._WAIT_FOR_STORE_LOADED_TEMPLATE).format(store_holder_cq=store_holder_cq)
        self.ensure_javascript_loaded()
        self._driver.execute_async_script(async_script)

        self._logger.debug("Store owned by '%s' loaded", store_holder_cq)

    def trigger_reload(self, store_holder_cq: str):
        """Triggers a reload on the specified store.

        Args:
            store_holder_cq (str): The component query to use to find the store holder.
        """
        script = self._RELOAD_STORE_TEMPLATE.format(store_holder_cq=store_holder_cq)
        self.ensure_javascript_loaded()
        self._driver.execute_script(script)

    def trigger_reload_and_wait(self, store_holder_cq: str):
        """Triggers a load on the specified store and waits for it to complete.

        Basically resets the store load count, triggers a reload and then waits for the store to
        show as loaded.

        Args:
            store_holder_cq (str): The component query to use to find the store holder.
        """
        self.reset_store_load_count(store_holder_cq)
        self.trigger_reload(store_holder_cq)
        self.wait_for_store_loaded(store_holder_cq)

    def check_store_contains(self, store_holder_cq: str, data: list[dict], should_only_contain_specified_data: bool = False):
        """Method that checks that the store contains the specified data, and optionally only the specified data.

        Can be used to check combobox data, say, or perhaps a grid.

        If the combobox or grid is paged, you will need to handle the paging yourself, checking the contents of each page
        as you go. That's well beyond the scope of what I can accomplish here!

        Throws an exception if the data does not match that which is expected.

        Args:
            store_holder_cq (str): The component query to use to find the store holder.
            data (list[dict]): The data we are looking for in the store specified as an array of
                               dictionary entries containing the 'name' and 'value' of the models
                               within the store.
                               Only data specified is checked for in the store's model data.
                               e.g.
                                    [
                                        {
                                            'name': 'Cat'
                                            'isSpecial': True
                                        },
                                        {
                                            'name': 'Dog'
                                        },
                                        {
                                            'name': 'Stoat',
                                            'id': 123
                                        }
                                    ]
            should_only_contain_specified_data (bool, optional): Indicates whether the store should only contain the passed in data.
                                                                 Defaults to False, so the store is allowed to contain other data.
        """
        self.wait_for_store_loaded(store_holder_cq)
        script = self._CHECK_STORE_CONTAINS_TEMPLATE.format(store_holder_cq=store_holder_cq, data=data, should_only_contain_specified_data=str(should_only_contain_specified_data).lower())
        self.ensure_javascript_loaded()
        self._driver.execute_script(script)
