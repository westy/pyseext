"""
Module that contains our FieldHelper class.
"""
import logging

from typing import Union, Any
from datetime import datetime

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from pyseext.component_query import ComponentQuery

from pyseext.has_referenced_javascript import HasReferencedJavaScript
from pyseext.core import Core
from pyseext.input_helper import InputHelper
from pyseext.store_helper import StoreHelper

class FieldHelper(HasReferencedJavaScript):
    """A class to help with interacting with Ext fields"""

    # Class variables
    _FIND_FIELD_INPUT_ELEMENT_TEMPLATE: str = "return globalThis.PySeExt.FieldHelper.findFieldInputElement('{form_cq}', '{name}')"
    """The script template to use to call the JavaScript method PySeExt.FieldHelper.findFieldInputElement
    Requires the inserts: {form_cq}, {name}"""

    _GET_FIELD_XTYPE_TEMPLATE: str = "return globalThis.PySeExt.FieldHelper.getFieldXType('{form_cq}', '{name}')"
    """The script template to use to call the JavaScript method PySeExt.FieldHelper.getFieldXType
    Requires the inserts: {form_cq}, {name}"""

    _GET_FIELD_VALUE_TEMPLATE: str = "return globalThis.PySeExt.FieldHelper.getFieldValue('{form_cq}', '{name}')"
    """The script template to use to call the JavaScript method PySeExt.FieldHelper.getFieldValue
    Requires the inserts: {form_cq}, {name}"""

    _GET_FIELD_DISPLAY_VALUE_TEMPLATE: str = "return globalThis.PySeExt.FieldHelper.getFieldDisplayValue('{form_cq}', '{name}')"
    """The script template to use to call the JavaScript method PySeExt.FieldHelper.getFieldDisplayValue
    Requires the inserts: {form_cq}, {name}"""

    _SET_FIELD_VALUE_TEMPLATE: str = "return globalThis.PySeExt.FieldHelper.setFieldValue('{form_cq}', '{name}', {value})"
    """The script template to use to call the JavaScript method PySeExt.FieldHelper.setFieldValue
    Requires the inserts: {form_cq}, {name}, {value}"""

    _IS_REMOTELY_FILTERED_COMBOBOX_TEMPLATE: str = "return globalThis.PySeExt.FieldHelper.isRemotelyFilteredComboBox('{form_cq}', '{name}')"
    """The script template to use to call the JavaScript method PySeExt.FieldHelper.isRemotelyFilteredComboBox
    Requires the inserts: {form_cq}, {name}"""

    _FOCUS_FIELD_TEMPLATE: str = "return globalThis.PySeExt.FieldHelper.focusField('{form_cq}', {index_or_name})"
    """The script template to use to call the JavaScript method PySeExt.FieldHelper.focusField
    Requires the inserts: {form_cq}, {index_or_name}"""

    _DOES_FIELD_HAVE_FOCUS_TEMPLATE: str = "return globalThis.PySeExt.FieldHelper.doesFieldHaveFocus('{form_cq}', {index_or_name})"
    """The script template to use to call the JavaScript method PySeExt.FieldHelper.doesFieldHaveFocus
    Requires the inserts: {form_cq}, {index_or_name}"""

    _SELECT_COMBOBOX_VALUE_TEMPLATE: str = "return globalThis.PySeExt.FieldHelper.selectComboBoxValue('{form_cq}', '{name}', {data})"
    """The script template to use to call the JavaScript method PySeExt.FieldHelper.selectComboBoxValue
    Requires the inserts: {form_cq}, {name}, {data}"""

    _GET_FIELD_RAW_VALUE: str = "return globalThis.PySeExt.FieldHelper.getFieldRawValue('{form_cq}', '{name}')"

    def __init__(self, driver: WebDriver):
        """Initialises an instance of this class

        Args:
            driver (WebDriver): The webdriver to use
        """
        self._logger = logging.getLogger(__name__)
        """The Logger instance for this class instance"""

        self._driver = driver
        """The WebDriver instance for this class instance"""

        self._action_chains = ActionChains(driver)
        """The ActionChains instance for this class instance"""

        self._core = Core(driver)
        """The `Core` instance for this class instance"""

        self._input_helper = InputHelper(driver)
        """The `InputHelper` instance for this class instance"""

        self._store_helper = StoreHelper(driver)
        """The `StoreHelper` instance for this class instance"""

        self._cq = ComponentQuery(driver)
        """The `ComponentQuery` instance for this class instance"""

        # Initialise our base class
        super().__init__(driver, self._logger)

    def find_field_input_element(self, form_cq: str, name: str) -> WebElement:
        """Attempts to get a field by name from the specified form panel

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field

        Returns:
            WebElement: The field's input element DOM element, or None if not found.
        """

        field_cq = self.get_field_component_query(form_cq, name)

        # Append enabled test
        field_cq = field_cq + '{isDisabled()===false}'

        # And wait until available
        self._cq.wait_for_single_query(field_cq)

        # Now get its input element
        script = self._FIND_FIELD_INPUT_ELEMENT_TEMPLATE.format(form_cq=form_cq, name=name)
        self.ensure_javascript_loaded()
        return self._driver.execute_script(script)

    def get_field_xtype(self, form_cq: str, name: str) -> str:
        """Attempts to get the xtype of a field by name from the specified form panel

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field

        Returns:
            str: The xtype of the field, or None if not found.
        """
        script = self._GET_FIELD_XTYPE_TEMPLATE.format(form_cq=form_cq, name=name)
        self.ensure_javascript_loaded()
        return self._driver.execute_script(script)

    def is_field_a_combobox(self, form_cq: str, name: str) -> bool:
        """Determine whether the field (by name) on the specified form panel is a combobox (or a subclass of it).

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field

        Returns:
            bool: True if the field is a combobox, False otherwise.
        """
        return self._cq.is_component_instance_of_class('Ext.form.field.ComboBox', self.get_field_component_query(form_cq, name))

    def is_field_a_text_field(self, form_cq: str, name: str) -> bool:
        """Determine whether the field (by name) on the specified form panel is a text field (or a subclass of it).
        Note that text areas, number fields, and date fields all inherit from text field.

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field

        Returns:
            bool: True if the field is a text field, False otherwise.
        """
        return self._cq.is_component_instance_of_class('Ext.form.field.Text', self.get_field_component_query(form_cq, name))

    def is_field_a_number_field(self, form_cq: str, name: str) -> bool:
        """Determine whether the field (by name) on the specified form panel is a number field (or a subclass of it).

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field

        Returns:
            bool: True if the field is a number field, False otherwise.
        """
        return self._cq.is_component_instance_of_class('Ext.form.field.Number', self.get_field_component_query(form_cq, name))

    def is_field_a_date_field(self, form_cq: str, name: str) -> bool:
        """Determine whether the field (by name) on the specified form panel is a date field (or a subclass of it).

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field

        Returns:
            bool: True if the field is a date field, False otherwise.
        """
        return self._cq.is_component_instance_of_class('Ext.form.field.Date', self.get_field_component_query(form_cq, name))

    def is_field_a_checkbox(self, form_cq: str, name: str) -> bool:
        """Determine whether the field (by name) on the specified form panel is a checkbox (or a subclass of it).

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field

        Returns:
            bool: True if the field is a checkbox, False otherwise.
        """
        return self._cq.is_component_instance_of_class('Ext.form.field.Checkbox', self.get_field_component_query(form_cq, name))

    def is_field_a_radio_field(self, form_cq: str, name: str) -> bool:
        """Determine whether the field (by name) on the specified form panel is a radio field (or a subclass of it).

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field

        Returns:
            bool: True if the field is a radio field, False otherwise.
        """
        return self._cq.is_component_instance_of_class('Ext.form.field.Radio', self.get_field_component_query(form_cq, name))

    def get_field_value(self, form_cq: str, name: str) -> Any:
        """Attempts to get the value of a field by name from the specified form panel

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field

        Returns:
            Any: The value of the field, or None if not found.
        """
        script = self._GET_FIELD_VALUE_TEMPLATE.format(form_cq=form_cq, name=name)
        self.ensure_javascript_loaded()

        value = self._driver.execute_script(script)

        if self.is_field_a_date_field(form_cq, name):
            if value:
                value = datetime.strptime(value, '%d/%m/%Y')

        return value

    def get_field_display_value(self, form_cq: str, name: str) -> Any:
        """Attempts to get the display value of a field by name from the specified form panel.

        Supported by comboboxes and display fields.

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field

        Returns:
            Any: The display value of the field, or None if not found or if the field does not have a display value.
        """
        script = self._GET_FIELD_DISPLAY_VALUE_TEMPLATE.format(form_cq=form_cq, name=name)
        self.ensure_javascript_loaded()
        return self._driver.execute_script(script)

    def get_field_raw_value(self, form_cq: str, name: str) -> Any:
        """Attempts to get the raw value of a field by name from the specified form panel.

        Can be used to get the value for a date field.

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field

        Returns:
            Any: The raw value of the field, or None if not found or if the field does not have a raw value.
        """
        script = self._GET_FIELD_RAW_VALUE.format(form_cq=form_cq, name=name)
        self.ensure_javascript_loaded()
        return self._driver.execute_script(script)

    def set_field_value(self, form_cq: str, name: str, value: Union[dict, float, str], delay: float = 0.1):
        """Sets the value for a field.

        If the field can be typed into by a user, and the value is typeable, then that is the approach taken.

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field.
            name (str): The name of the field.
            value (Union[dict, float, str]): The value for the field.

                                             If the value is a number or string then it is typed into the field where possible,
                                             otherwise the value is set directly.

                                             If the value is a dictionary then either it, or it's value member is taken to be model
                                             data to select in a combobox.

                                             If the combobox is remotely filtered then it is expected that both a value member and
                                             a filterText member is specified, where the filterText is typed into the combobox, then
                                             the value selected.

                                             If the value is supplied as a dictionary and the field is not a store holder then
                                             an exception is thrown.
            delay (float): The delay in seconds to use between keystrokes when typing into a field. Defaults to 0.1 second.
        """
        # Only used for radiogroup controls now, but xtype still useful to throw a better error if field not found.
        field_xtype = self.get_field_xtype(form_cq, name)

        if field_xtype:
            # Field found!
            field_value = self._core.try_get_object_member(value, 'value', value)

            # Now need to set it's value
            if self.is_field_a_combobox(form_cq, name):
                is_combo_remote = self._is_field_remotely_filtered_combobox(form_cq, name)
                is_value_a_dict = isinstance(field_value, dict)

                if is_combo_remote:
                    if not is_value_a_dict:
                        # We want to type into the combobox, to filter it, and wait for it to load.
                        # Once loaded we expect to have a single value that will end up selected.

                        # Reset the store load count
                        combobox_cq = self.get_field_component_query(form_cq, name)
                        self._store_helper.reset_store_load_count(combobox_cq)

                        # Filter it
                        field = self.find_field_input_element(form_cq, name)
                        self._input_helper.type_into_element(field, field_value, disable_realistic_typing=True)

                        # Wait for the store to load
                        self._store_helper.wait_for_store_loaded(combobox_cq)

                        # Often (especially when local) the load count will be incremented several times
                        # before the store load has actually triggered and completed.
                        # To guard against this, wait for any pending Ajax calls to complete, then check
                        # if the store has loaded
                        self._core.wait_for_no_ajax_requests_in_progress(recheck_time_if_false=1)

                        # Seems we need to tab off or sometimes the value will not stick?!
                        self._input_helper.type_tab()
                    else:
                        # We are expecting some filter text
                        filter_text = self._core.try_get_object_member(value, 'filterText')

                        if not filter_text:
                            raise Core.ArgumentException("value", "We were expecting the argument '{name}' to have a 'filterText' member, but it is missing.")

                        # Reset the store load count
                        combobox_cq = self.get_field_component_query(form_cq, name)
                        self._store_helper.reset_store_load_count(combobox_cq)

                        # Filter it
                        field = self.find_field_input_element(form_cq, name)
                        self._input_helper.type_into_element(field, filter_text, disable_realistic_typing=True)

                        # Wait for the store to load
                        self._store_helper.wait_for_store_loaded(combobox_cq)

                        # Often (especially when local) the load count will be incremented several times
                        # before the store load has actually triggered and completed.
                        # To guard against this, wait for any pending Ajax calls to complete.
                        self._core.wait_for_no_ajax_requests_in_progress(recheck_time_if_false=1)

                        was_value_selected = self.select_combobox_value(form_cq, name, field_value)

                        if not was_value_selected:
                            raise FieldHelper.RecordNotFoundException(form_cq, name, field_value)
                else:
                    if not is_value_a_dict:
                        # We can just type into the combobox
                        field = self.find_field_input_element(form_cq, name)
                        self._input_helper.type_into_element(field, field_value, delay)

                        # Seems we need to tab off or sometimes the value will not stick?!
                        self._input_helper.type_tab()
                    else:
                        was_value_selected = self.select_combobox_value(form_cq, name, field_value)

                        if not was_value_selected:
                            raise FieldHelper.RecordNotFoundException(form_cq, name, field_value)

            elif self.is_field_a_text_field(form_cq, name):
                # Field can be typed into
                field = self.find_field_input_element(form_cq, name)
                self._input_helper.type_into_element(field, field_value)

            # Still using xtype for testing for radiogroup controls, since name tends to be
            # shared between group and contained radios, meaning check fails.
            # Pretty unlikely to ever subclass a radiogroup class anyway, and if did would almost
            # certainly have the same suffix (we do).
            elif (field_xtype.endswith('radiogroup') or
                self.is_field_a_checkbox(form_cq, name) or
                self.is_field_a_radio_field(form_cq, name)):
                # Directly set the value on the field
                self.set_field_value_directly(form_cq, name, field_value)
            else:
                raise FieldHelper.UnsupportedFieldXTypeException(form_cq, name, field_xtype)
        else:
            raise FieldHelper.FieldNotFoundException(form_cq, name)

    def set_field_value_directly(self, form_cq: str, name: str, value: Union[int, str]):
        """Sets the value for a field using Ext's setValue method.

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field
            value (Union[int, str]): The value for the field.
        """
        # If value is a string then we want to quote it in our script
        if isinstance(value, str):
            value = f"'{value}'"

        # If value is a boolean we want to force it to lowercase
        if isinstance(value, bool):
            value = str(value).lower()

        script = self._SET_FIELD_VALUE_TEMPLATE.format(form_cq=form_cq, name=name, value=value)
        self.ensure_javascript_loaded()
        self._driver.execute_script(script)

    def focus_field(self, form_cq: str, index_or_name: Union[int, str], check_has_focus_after: bool = True):
        """Method to focus on a field on a form by (zero-based) index or name.

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            index_or_name (Union[int, str]): The zero-based index or name of the field to focus.
            check_has_focus_after (bool): Indicates whether to check that the field is focused afterwards. Defaults to True.
        """
        # If value is a string then we want to quote it in our script
        if isinstance(index_or_name, str):
            index_or_name = f"'{index_or_name}'"

        script = self._FOCUS_FIELD_TEMPLATE.format(form_cq=form_cq, index_or_name=index_or_name)
        self.ensure_javascript_loaded()

        self._logger.info("Focusing field %s on form '%s'", index_or_name, form_cq)
        self._driver.execute_script(script)

        if check_has_focus_after:
            has_focus = self.does_field_have_focus(form_cq, index_or_name)

            if not has_focus:
                self._logger.debug("Field %s on form '%s' does not have focus!", index_or_name, form_cq)
                # Try again (can't hurt)
                self._driver.execute_script(script)

            else:
                self._logger.debug("Field %s on form '%s' has focus!", index_or_name, form_cq)

    def does_field_have_focus(self, form_cq: str, index_or_name: Union[int, str]) -> bool:
        """Determines whether focus is on a field on a form by (zero-based) index or name.

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            index_or_name (Union[int, str]): The zero-based index or name of the field.

        Returns:
            bool: True if the field has focus, False otherwise.
        """
        # If value is a string then we want to quote it in our script
        if isinstance(index_or_name, str):
            index_or_name = f"'{index_or_name}'"

        script = self._DOES_FIELD_HAVE_FOCUS_TEMPLATE.format(form_cq=form_cq, index_or_name=index_or_name)
        self.ensure_javascript_loaded()
        return self._driver.execute_script(script)

    def wait_until_field_has_focus(self, form_cq: str, index_or_name: Union[int, str], timeout: float = 10):
        """Waits until the focus is on a field on a form by (zero-based) index or name.

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            index_or_name (Union[int, str]): The zero-based index or name of the field.
            timeout (float): Number of seconds before timing out (default 10)
        """
        WebDriverWait(self._driver, timeout).until(FieldHelper.FieldHasFocusExpectation(form_cq, index_or_name))

    def get_field_component_query(self, form_cq: str, name: str):
        """Builds the component query for a field on a form.

        This is useful, since allows you to interact with a field using component query, so can
        utilise the methods in StoreHelper, say.

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field.
        """
        # Need to use component rather than field since need to be able to query for radiogroup and checkbox group.
        return f'{form_cq} component[name="{name}"]'

    def check_field_value(self, form_cq: str, name: str, value: Any) -> bool:
        """Method that checks that the value of the specified field is that specified.

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field.
            name (str): The name of the field
            value (Any): The value that we expect the field to have.

        Returns:
            bool: True if the value of the field matches the expected, False otherwise.
        """
        field_value = self.get_field_value(form_cq, name)

        return field_value == value

    def select_combobox_value(self, form_cq: str, name: str, data: dict) -> bool:
        """Selects a value on a combobox field by finding a record with the specified data.
        All members of the data object must match a record in the store.

        Waits until the combobox has finished loading first, and ensures that the select
        event is fired on the combobox if the record is found.

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field
            data (dict): The data to find in the store and select.

        Returns:
            True if the value was found and selected, False otherwise.
        """
        self._store_helper.wait_for_store_loaded(self.get_field_component_query(form_cq, name))

        script = self._SELECT_COMBOBOX_VALUE_TEMPLATE.format(form_cq=form_cq, name=name, data=data)
        self.ensure_javascript_loaded()
        return self._driver.execute_script(script)

    def _is_field_remotely_filtered_combobox(self, form_cq: str, name: str) -> bool:
        """Attempts to find a field by name from the specified form panel, and determine whether
        it is a remotely filtered combobox.

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field

        Returns:
            bool: True if the field was found, and is a remotely filtered combobox. False otherwise.
        """
        script = self._IS_REMOTELY_FILTERED_COMBOBOX_TEMPLATE.format(form_cq=form_cq, name=name)
        self.ensure_javascript_loaded()
        return self._driver.execute_script(script)

    class FieldNotFoundException(Exception):
        """Exception class thrown when we failed to find the specified field"""

        def __init__(self, form_cq: str, name: str, message: str = "Failed to find field named '{name}' on form with CQ '{form_cq}'."):
            """Initialises an instance of this exception

            Args:
                form_cq (str): The CQ used to find the form
                name (str): The name of the field
                message (str, optional): The exception message. Defaults to "Failed to find field named '{name}' on form with CQ '{form_cq}'.".
            """
            self.message = message
            self._form_cq = form_cq
            self._name = name

            super().__init__(self.message)

        def __str__(self):
            """Returns a string representation of this exception"""
            return self.message.format(name=self._name, form_cq=self._form_cq)

    class UnsupportedFieldXTypeException(Exception):
        """Exception class thrown when we have been asked to perform an action that is not
        supported for the given field xtype.
        """

        def __init__(self,
                     form_cq: str,
                     name: str,
                     xtype: str,
                     message: str = "The field named '{name}' on form with CQ '{form_cq}' is of an xtype '{xtype}' which is not supported for the requested operation."):
            """Initialises an instance of this exception

            Args:
                form_cq (str): The CQ used to find the form
                name (str): The name of the field
                xtype (str): The xtype of the field.
                message (str, optional): The exception message.
                                        Defaults to "The field named '{name}' on form with CQ '{form_cq}' is of an xtype '{xtype}' which is not supported for the requested operation."
            """
            self.message = message
            self._form_cq = form_cq
            self._name = name
            self._xtype = xtype

            super().__init__(self.message)

        def __str__(self):
            """Returns a string representation of this exception"""
            return self.message.format(name=self._name, form_cq=self._form_cq, xtype=self._xtype)

    class RecordNotFoundException(Exception):
        """Exception class thrown when we failed to find the specified record in the a combobox"""

        def __init__(self, form_cq: str, name: str, data: dict, message: str = "Failed to find record with data {data} in combobox named '{name}' on form with CQ '{form_cq}'."):
            """Initialises an instance of this exception

            Args:
                form_cq (str): The CQ used to find the form
                name (str): The name of the combobox
                data (dict): The data for the record we were looking for.
                message (str, optional): The exception message. Defaults to "Failed to find record with data {data} in combobox named '{name}' on form with CQ '{form_cq}'.".
            """
            self.message = message
            self._form_cq = form_cq
            self._name = name
            self._data = data

            super().__init__(self.message)

        def __str__(self):
            """Returns a string representation of this exception"""
            return self.message.format(data=self._data, name=self._name, form_cq=self._form_cq)

    class FieldHasFocusExpectation:
        """ An expectation for checking that the specified field has focus"""

        def __init__(self, form_cq: str, index_or_name: Union[int, str]):
            """Initialises an instance of this class.

            Args:
                form_cq (str): The component query that identifies the form panel in which to look for the field
                index_or_name (Union[int, str]): The zero-based index or name of the field.
            """
            self._form_cq = form_cq
            self._index_or_name = index_or_name

        def __call__(self, driver):
            """Method that determines whether a CQ is found
            """
            return FieldHelper(driver).does_field_have_focus(self._form_cq, self._index_or_name)
