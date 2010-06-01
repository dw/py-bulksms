'''
BulkSMS/HTTPCallback.py: Handle user HTTP relay requests.
'''

__author__ = 'David Wilson'

from CoreBulkSMS import BulkSMSException
import cgi



class AuthenticationException(BulkSMSException):
    '''
    Exception. Raised when we could not authenticate the incoming HTTP
    relay connection.
    '''

    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return str(self.reason)




class FormatException(BulkSMSException):
    '''
    Exception. Raised when we receieve corrupt data from BulkSMS.
    '''

    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return str(self.reason)




def fetch_reply(auth_field = None, auth_value = None):
    '''
    Utilise the cgi module to read a reply from BulkSMS from the current
    CGI environment. If <auth_field> and <auth_value> are not None, then
    perform a simple authentication using them. Return a dict containing
    the values specified in the EAPI documentation on success. Raise an
    exception on failure.
    '''


    # For two years I have hacked in Python happily. Then I used the cgi
    # module. We can get away with a dict here because BulkSMS don't reuse
    # field names.

    silly_form = cgi.FieldStorage()
    reply = {}
    form = {}

    for key in silly_form.keys():
        form[key] = silly_form[key].value

    # Get out of my namespace, punk.
    del silly_form


    if auth_field is not None and auth_value is not None:
        value = form.getfirst(auth_field, None)

        if auth is None:
            raise AuthenticationException(\
                'Missing auth field: %r' % ( auth_field ))

        if value != auth_value:
            raise AuthenticationException(\
                'Authentication failed.')



    try:
        reply['msisdn'] = form.get('msisdn')
        reply['sender'] = form.get('sender')
        reply['message'] = form.get('message')
        reply['msg_id'] = int(form.get('msg_id'))
        reply['referring_msg_id'] = int(form.get['referring_msg_id'])

    except KeyError, e:
        raise FormatException(\
            'HTTP relay message missing field %r' % ( e.args[0] ))

    except ValueError, e:
        raise FormatException(\
            'HTTP relay msg_id or referring_msg_id not an integer.')


    return reply
