#!/usr/bin/env python

'''
BulkSMS.py: Send messages via BulkSMS.co.uk.
'''

__author__ = 'David M. Wilson <dw-BulkSMS@botanicus.net>'
__version__ = '0.3'



# Was CoreBulkSMS really such a good idea?
# TODO(dmw): add __all__ to CoreBulkSMS.

from CoreBulkSMS import \
    BulkSMSException, MessageLengthException, AuthenticationException, \
    DataValidationException, InsufficientCreditsException, \
    DuplicateMessageException, QuotaException, MessageNotFoundException, \
    InternalFatalError, UnknownException, CommunicationException, \
    \
    format_credits, BulkSMS
