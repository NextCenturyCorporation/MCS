import logging
from typing import Any

from marshmallow.fields import Boolean

logger = logging.getLogger(__name__)


class Validation():
    '''
    Support for tests and conditions on validation numbers and strings.
    '''
    @staticmethod
    def is_in_range(value, min_value, max_value, default_value, label=None):
        """
        Returns if the given value is within the given min and max; if not,
        returns the given default.

        Parameters
        ----------
        value : number
            The input value.
        min_value : number
            The min value.
        max_value : number
            The max value.
        default_value : number
            The default value.
        label : string
            A label for the input value.  If given, and if the input
            value is not within the range, will print an error.

        Returns
        -------
        number
        """
        if min_value <= value <= max_value:
            return value

        if label is not None:
            logger.debug(
                f'Value of {label} needs to be between '
                f'{min_value} and {max_value}. '
                f'Current value {value} '
                f'will be reset to {default_value}.')
        return default_value

    @staticmethod
    def is_number(value: Any, label=None) -> Boolean:
        """
        Returns if the given value is a number.

        Parameters
        ----------
        value :
            The input value.
        label : string
            A label for the input value.  If given, and if the
            input value is not a number, will print an error.

        Returns
        -------
        boolean
        """
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            if label is not None:
                logger.debug(f'Value of {label}'
                             f' needs to be a number. Will be set to 0.')
            return False
