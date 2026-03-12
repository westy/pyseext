"""
Module that contains our InputHelper class.
"""
import logging
import random
from typing import Union

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

class InputHelper:
    """A class to help with user input."""

    INPUT_SLEEP_MINIMUM: float = 0.0001
    """The minimum amount of time in seconds to wait between key presses when typing or other inputs. Defaults to 0.0001 seconds."""

    INPUT_SLEEP_MAXIMUM: float = 0.002
    """The maximum amount of time in seconds to wait between key presses when typing or other inputs. Defaults to 0.002 seconds."""

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

    def type_into_element(self, element: WebElement, text: str, delay: float = 0.1, tab_off: Union[bool, None] = False, disable_realistic_typing: bool = True, clear_first: bool = True):
        """Types into an input element in a realistic manner, unless web driver is remote.

        Args:
            element (WebElement): The element to type into.
            text (str): The text to type.
            delay (float, optional): The number of seconds to delay after typing. Defaults to 0.1 second.
            tab_off (bool, optional): Indicates whether to tab off the field after typing, and delay. Defaults to False.
            disable_realistic_typing (bool, optional): Indicates whether to disable typing in a 'realistic' manner when not remote. Defaults to True.
            clear_first (bool, optional): Indicates whether to clear the element first. Defaults to True.
        """
        # If text is None then use empty string
        if text is None:
            text = ''

        # Ensure text really is a string
        text = str(text)

        if clear_first:
            # Clear the element first, in case has something in it
            element.clear()

        # First move to and click on element to give it focus
        self._action_chains.move_to_element(element)
        self._action_chains.click()
        self._action_chains.perform()
        # this pause was added to avoid a scenario where its is not ready to type and to avoid incorrect characters being typed in.
        # This was observed in a test that was typing into a field and then immediately tabbing off, which caused the tab to be typed into the field instead of tabbing off.
        self._action_chains.pause(delay)
        # Now type each character
        self.type(text, disable_realistic_typing)

        if delay:
            # after typing into the field it waits before tabbing off
            self._action_chains.pause(delay)
            self._action_chains.perform()

        if tab_off:
            self.type_tab()

    def type(self, text: str, disable_realistic_typing: bool = True):
        """Types into the currently focused element in a realistic manner, unless our webdriver is remote, then just sends the complete string.

        Args:
            text (str): The text to type.
            disable_realistic_typing (bool, optional): Indicates whether to disable typing in a 'realistic' manner when not remote. Defaults to True.
        """

        # If we are remote, then typing a character at a time involves a roundtrip for every character.
        # This is not ideal, since slows down the test massively.
        if not disable_realistic_typing and not self._driver._is_remote: # pylint: disable=protected-access
            for character in text:
                self._action_chains.send_keys(character)
                self._action_chains.pause(random.uniform(self.INPUT_SLEEP_MINIMUM, self.INPUT_SLEEP_MAXIMUM))
                self._action_chains.perform()
        else:
            self._action_chains.send_keys(text)
            self._action_chains.perform()

    def type_tab(self, pause_time: Union[float, None] = None):
        """Type a tab character into the currently focused element.

        Args:
            pause_time (float, optional): The amount of time to pause after hitting tab (when web driver is not remote).
                                          Defaults to None, in which case a random wait time is used between INPUT_SLEEP_MINIMUM and INPUT_SLEEP_MAXIMUM.
        """
        self._action_chains.send_keys(Keys.TAB)

        if not self._driver._is_remote: # pylint: disable=protected-access
            if pause_time is None:
                pause_time = random.uniform(self.INPUT_SLEEP_MINIMUM, self.INPUT_SLEEP_MAXIMUM)

            self._action_chains.pause(pause_time)

        self._action_chains.perform()

    def type_return(self, pause_time: Union[float, None] = None):

        """Types a return character into the currently focused element.

        Args:
            pause_time (float, optional): The amount of time to pause after hitting return (when web driver is not remote).
                                          Defaults to None, in which case a random wait time is used between INPUT_SLEEP_MINIMUM and INPUT_SLEEP_MAXIMUM.
        """
        self._action_chains.send_keys(Keys.RETURN)

        if not self._driver._is_remote: # pylint: disable=protected-access
            if pause_time is None:
                pause_time = random.uniform(self.INPUT_SLEEP_MINIMUM, self.INPUT_SLEEP_MAXIMUM)

            self._action_chains.pause(pause_time)

        self._action_chains.perform()

    def type_escape(self, pause_time: Union[float, None] = None):
        """Types an escape character into the currently focused element.

        Args:
            pause_time (float, optional): The amount of time to pause after hitting escape (when web driver is not remote).
                                          Defaults to None, in which case a random wait time is used between INPUT_SLEEP_MINIMUM and INPUT_SLEEP_MAXIMUM.
        """
        self._action_chains.send_keys(Keys.ESCAPE)

        if not self._driver._is_remote: # pylint: disable=protected-access
            if pause_time is None:
                pause_time = random.uniform(self.INPUT_SLEEP_MINIMUM, self.INPUT_SLEEP_MAXIMUM)

            self._action_chains.pause(pause_time)

        self._action_chains.perform()

    def type_delete(self, pause_time: Union[float, None] = None):
        """Types a delete character into the currently focused element.

        Args:
            pause_time (float, optional): The amount of time to pause after hitting delete (when web driver is not remote).
                                          Defaults to None, in which case a random wait time is used between INPUT_SLEEP_MINIMUM and INPUT_SLEEP_MAXIMUM.
        """
        self._action_chains.send_keys(Keys.DELETE)

        if not self._driver._is_remote: # pylint: disable=protected-access
            if pause_time is None:
                pause_time = random.uniform(self.INPUT_SLEEP_MINIMUM, self.INPUT_SLEEP_MAXIMUM)

            self._action_chains.pause(pause_time)

        self._action_chains.perform()
