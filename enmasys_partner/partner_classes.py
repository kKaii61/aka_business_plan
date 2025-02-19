import logging

from odoo.exceptions import ValidationError, UserError, AccessDenied, AccessError

_logger = logging.getLogger(__name__)


class PartnerPartner:

    def __init__(self):
        pass


class PartnerException(PartnerPartner):
    _partner_exception = None

    def __init__(self, exception=None):
        self._partner_exception = exception
        super(PartnerException, self).__init__()

    def catch_and_handle_exception(self, raise_if_necessary=True):
        exception = self._partner_exception
        _logger.exception(msg=exception)
        _exception = UserError(exception)
        if not raise_if_necessary:
            return
        if isinstance(exception, ValidationError):
            raise ValidationError(exception)
        if isinstance(exception, AccessDenied):
            raise AccessDenied(exception)
        if isinstance(exception, AccessError):
            raise AccessError(exception)
        raise _exception

    @classmethod
    def raise_exception_directly(cls, message, exception_type='validation'):
        directly_types = {
            'validation': ValidationError(message),
            'user_error': UserError(message),
            'access_error': AccessError(message),
            'access_denied': AccessDenied(message)
        }
        raise directly_types.get(exception_type, directly_types.get('validation'))
