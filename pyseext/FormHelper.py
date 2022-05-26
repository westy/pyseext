import random
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from pyseext.HasReferencedJavaScript import HasReferencedJavaScript
from pyseext.ButtonHelper import ButtonHelper

class FormHelper(HasReferencedJavaScript):
    """A class to help with interacting with Ext form panels and forms
    """

    # Class variables
    _FIND_FIELD_INPUT_ELEMENT_TEMPLATE = "return globalThis.PySeExt.FormHelper.findFieldInputElement('{form_cq}', '{name}')"
    _GET_FIELD_XTYPE_TEMPLATE = "return globalThis.PySeExt.FormHelper.getFieldXType('{form_cq}', '{name}')"
    _SET_CHECKBOX_VALUE_TEMPLATE = "return globalThis.PySeExt.FormHelper.setCheckboxValue('{form_cq}', '{name}', {checked})"
    _SET_FIELD_NUMERIC_VALUE_TEMPLATE = "return globalThis.PySeExt.FormHelper.setFieldNumericValue('{form_cq}', '{name}', {value})"

    def __init__(self, driver):
        """Initialises an instance of this class

        Args:
            driver (selenium.webdriver): The webdriver to use
        """
        self._driver = driver
        self._button_helper = ButtonHelper(driver)
        self._action_chains = ActionChains(driver)

        # Initialise our base class
        super().__init__(driver)

    def find_field_input_element(self, form_cq, name):
        """Attempts to get a field by name from the specified form panel

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field

        Returns:
            selenium.webdriver.remote.webelement: The field's input element DOM element, or None if not found.
        """
        script = self._FIND_FIELD_INPUT_ELEMENT_TEMPLATE.format(form_cq=form_cq, name=name)
        return self._driver.execute_script(script)

    def get_field_xtype(self, form_cq, name):
        """Attempts to get the xtype of a field by name from the specified form panel

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field

        Returns:
            str: The xtype of the field, or None if not found.
        """
        script = self._GET_FIELD_XTYPE_TEMPLATE.format(form_cq=form_cq, name=name)
        return self._driver.execute_script(script)

    def set_form_values(self, form_cq, field_values):
        """Sets the values on the specified form panel

        Args:
            field_values (dict): Dictionary containing the 'name' and 'value' of the fields.
                                 The values can be strings, numbers or an object containing:
                                  - value (Any): The value for the field
                                  - delay (int): Number of seconds to delay after setting a value (a botch for remote combos at the moment)
                                  - tab_off (bool): Indicates whether to tab off the field after typing (another botch for remote combos)
        """
        if not type(field_values) is dict:
            raise TypeError("Parameter 'field_values' is not of type 'dict'")

        def get_field_config_member(value, member, default=None):
            """Gets the member from a field config.

            Args:
                value (Any): The value or value config for the field.
                member (str): The member we're after.
                default (Any, optional): The default to return if not found. Defaults to None.

            Returns:
                Any: The value of the config, or the default if not found.
            """
            if isinstance(value, dict):
                return value.get(member, default)
            else:
                return default

        for field_name in field_values.keys():
            field_xtype = self.get_field_xtype(form_cq, field_name)

            if field_xtype:
                # Field found!
                value_or_config = field_values[field_name]

                field_value = get_field_config_member(value_or_config, 'value', value_or_config)
                delay = get_field_config_member(value_or_config, 'delay')
                tab_off = get_field_config_member(value_or_config, 'tab_off', False)

                # Now need to set it's value
                if (field_xtype.endswith('textfield') or
                    field_xtype.endswith('number') or
                    field_xtype.endswith('datefield') or
                    ((field_xtype.endswith('combo') or field_xtype.endswith('combobox')) and
                      isinstance(field_value, str))):
                    # Field can be typed into
                    field = self.find_field_input_element(form_cq, field_name)
                    self.type_into_element(field, field_value, delay, tab_off)
                elif field_xtype.endswith('checkbox'):
                    self.set_checkbox_value(form_cq, field_name, field_value)
                elif (field_xtype.endswith('combo') or
                    field_xtype.endswith('combobox')):
                    # We want to directly set the value on the combo rather than type it in
                    self.set_field_numeric_value(form_cq, field_name, field_value)
                else:
                    raise FormHelper.UnsupportedFieldXTypeException(form_cq, field_name, field_xtype)
            else:
                raise FormHelper.FieldNotFoundException(form_cq, field_name)

    def submit_by_button(self, form_cq, text = 'Ok'):
        """Submits a form by clicking on it's submit button.

        Args:
            form_cq (str): The component query that identifies the form panel to submit.
            text (str, optional): The text on the submit button. Defaults to 'Ok'.
        """
        self._button_helper.click_button_by_text(text, form_cq)

    def set_checkbox_value(self, form_cq, field_name, checked=True):
        """Sets the checked value for a checkbox.

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field
            checked (bool, optional): The checked value for the checkbox. Defaults to True.
        """
        script = self._SET_CHECKBOX_VALUE_TEMPLATE.format(form_cq=form_cq, name=field_name, checked=str(checked).lower())
        return self._driver.execute_script(script)

    def set_field_numeric_value(self, form_cq, field_name, value):
        """Sets the value for a field to a numeric value.

        Args:
            form_cq (str): The component query that identifies the form panel in which to look for the field
            name (str): The name of the field
            value (int): The value for the field.
        """
        script = self._SET_FIELD_NUMERIC_VALUE.format(form_cq=form_cq, name=field_name, value=value)
        return self._driver.execute_script(script)

    def type_into_element(self, element, text, delay=None, tab_off=False):
        """Types into an input element in a more realistic manner.

        Args:
            element (selenium.webdriver.remote.webelement): The element to type into.
            text (str): The text to type.
            delay (int): The number of seconds to delay after typing.
            tab_off (bool): Indicates whether to tab off the field after typing, and delay.
        """
        # Ensure text really is a string
        text = str(text)

        # First move to and click on element to give it focus
        self._action_chains.move_to_element(element)
        self._action_chains.click()
        self._action_chains.perform()

        # Now type each character
        for character in text:
            self._action_chains.send_keys(character)
            self._action_chains.perform()
            time.sleep(random.uniform(0.0001, 0.002))

        if delay:
            time.sleep(delay)

        if tab_off:
            self._action_chains.send_keys(Keys.TAB)
            self._action_chains.perform()

    class FieldNotFoundException(Exception):
        """Exception class thrown when we failed to find the specified field
        """

        def __init__(self, form_cq, field_name, message="Failed to find field named '{field_name}' on form with CQ '{form_cq}'."):
            """Initialises an instance of this exception

            Args:
                form_cq (str): The CQ used to find the form
                field_name (str): The name of the field
                message (str, optional): The exception message. Defaults to "Failed to find field named '{field_name}' on form with CQ '{form_cq}'.".
            """
            self.message = message
            self._form_cq = form_cq
            self._field_name = field_name

            super().__init__(self.message)

        def __str__(self):
            """Returns a string representation of this exception
            """
            return self.message.format(field_name=self._field_name, form_cq=self._form_cq)

    class UnsupportedFieldXTypeException(Exception):
        """Exception class thrown when we have been asked to perform an action that is not
        supported for the given field xtype.
        """

        def __init__(self, form_cq, field_name, xtype, message="The field named '{field_name}' on form with CQ '{form_cq}' is of an xtype '{xtype}' which is not supported for the requested operation."):
            """Initialises an instance of this exception

            Args:
                form_cq (str): The CQ used to find the form
                field_name (str): The name of the field
                xtype (str): The xtype of the field.
                message (str, optional): The exception message. Defaults to "The field named '{field_name}' on form with CQ '{form_cq}' is of an xtype '{xtype}' which is not supported for the requested operation."
            """
            self.message = message
            self._form_cq = form_cq
            self._field_name = field_name
            self._xtype = xtype

            super().__init__(self.message)

        def __str__(self):
            """Returns a string representation of this exception
            """
            return self.message.format(field_name=self._field_name, form_cq=self._form_cq, xtype=self._xtype)