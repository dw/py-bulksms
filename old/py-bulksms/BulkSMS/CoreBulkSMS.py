'''
BulkSMS/CoreBulkSMS.py: Core BulkSMS package functionality.
'''

__author__ = 'David M. Wilson <dw-CoreBulkSMS.py@botanicus.net>'
__version__ = '0.1'

import urllib, urllib2, time, PhoneBook




class BulkSMSException(Exception):
    """
    Exception. Base class for all BulkSMS.co.uk exceptions.
    """

    pass




class MessageLengthException(BulkSMSException):
    """
    Exception. Raised when an SMS message is too long to transmit.
    """

    def __init__(self, len, max):
        self.len = len
        self.max = max

    def __str__(self):
        return \
            "SMS message too long. Maximum: %d, length: %d" % \
            ( self.max, self.len )




class AuthenticationException(BulkSMSException):
    """
    Exception. Raised when BulkSMS.co.uk refuse our (<username>, <password>).
    """

    def __init__(self, description):
        self.status_code = 23
        self.status_description = description

    def __str__(self):
        return "Authentication failure: %s" % self.status_description




class DataValidationException(BulkSMSException):
    """
    Exception. Raised when BulkSMS.co.uk indicate our supplied values were
    incorrect.
    """

    def __init__(self, description):
        self.status_code = 24
        self.status_description = description

    def __str__(self):
        return "Data validation failed: %s" % self.status_description




class InsufficientCreditsException(BulkSMSException):
    """
    Exception. Raised when BulkSMS.co.uk indicate we do not have enough credits
    to send a message.
    """

    def __init__(self, code, description):
        self.status_code = 24
        self.status_description = description

    def __str__(self):
        return "Insufficient credit: %s" % self.status_description




class DuplicateMessageException(BulkSMSException):
    """
    Exception. Raised when BulkSMS.co.uk indicate that this message is a
    duplicate and nodup is enabled.
    """

    def __init__(self):
        self.status_code = 50

    def __str__(self):
        return "Duplicate message detected."




class QuotaException(BulkSMSException):
    """
    Exception. Raised when BulkSMS.co.uk indicate we have reached our
    transmission quota.
    """

    def __init__(self, code, description):
        self.status_code = code
        self.status_description = description

    def __str__(self):
        return "Transmission quota reached: %s" % self.status_description




class MessageNotFoundException(BulkSMSException):
    """
    Exception. Raised when BulkSMS.co.uk cannot find a msg_id we have requested.
    """

    def __init__(self):
        self.status_code = 1001

    def __str__(self):
        return "Message not found."




class InternalFatalError(BulkSMSException):
    """
    Exception. Raised when an internal fatal error occurs at BulkSMS.co.uk.
    """

    def __init__(self):
        self.status_code = 22

    def __str__(self):
        return "Internal fatal error."




class UnknownException(BulkSMSException):
    """
    Exception. Raised when an unknown status message is returned by BulkSMS.co.uk.
    """

    def __init__(self, status_code, status_description = None):
        self.status_code = int(status_code)
        self.status_description = status_description

    def __str__(self):
        if not self.status_description:
            return "Unknown error %d occured." % self.status_code

        return "Unknown error %d occurred: '%s'" % \
            ( self.status_code, self.status_description )




class CommunicationException(BulkSMSException):
    """
    Exception. Raised when we could not talk to BulkSMS.co.uk.
    """

    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return str(self.reason)



def format_credits(credits):
    """
    Return a string representation of the floating point number <credits>
    formatted as BulkSMS.co.uk format their floats.
    """

    return "%3.2f" % credits





class BulkSMS:
    """
    Main SMS server communication class. Allows transmission of one or multiple
    messages, and confirmation of delivery.

    <sender> is the sender field of the message; if numeric, maximum 14 bytes,
    if alphanumeric, maximum 11 bytes.

    <msg_class> is the message class. A value of 0 indicates a flash message, 2
    indicates a normal SMS.

    <dca> is the Data Coding Alphabet. One of "7bit", "8bit", or "16bit".
    Messages may be a maximum of 280 characters for 7bit and 8bit types.

    <want_report> specifies whether or not we would like a delivery report.

    <cost_route> is an integer ranging from 1, lowest cost to 3, better quality.
    Higher quality routes may deliver more reliably or faster.

    <msg_id> is currently unused. It will be your unique ID for the message.

    <nodup> indicates that if this (<sender>, <message>) tuple has been seen in
    the last 10 minutes, the message should not be sent.

    <transient_wait> is the number of seconds we should wait before retrying
    requests that failed due to transient errors.

    <transient_retries> is the number of times we should retry a request before
    giving up due to transient errors. Set to None to fail immediately.

    <poll_time> is the maximum amount of time in seconds that we will spend
    trying to get delivery reports.

    <poll_wait> is the amount of time in seconds that we will wait between
    requests for delivery reports.

    <repliable> indicates that this SMS should initiate a 2-way SMS if at
    all possible.
    """

    _server = 'www.bulksms.co.uk'
    _max_lengths = { '7bit': 160, '8bit': 280, '16bit': 280 }
    _bare_request = ( 'username', 'password' )

    _valid_options = [
        ( 'sender', str ),         ( 'msg_class', int ),
        ( 'dca', str ),            ( 'want_report', bool ),
        ( 'cost_route', int ),     ( 'nodup', bool ),
        ( 'transient_wait', int ), ( 'transient_retries', int ),
        ( 'poll_time', int ),      ( 'poll_wait', int ),
        ( 'phonebook', PhoneBook.BasePhoneBook ),
        ( 'secure_repr', bool ),   ( 'repliable', int )
    ]

    _ports_paths = {
        'send_sms':          ( 5567, '/eapi/submission/send_sms/1/1.1' ),
        'quote_sms':         ( 7512, '/eapi/1.0/quote_sms.mc' ),
        'get_report':        ( 7512, '/eapi/1.0/get_report.mc' ),
        'get_credits':       ( 7512, '/eapi/1.0/get_credits.mc' ),
    }




    def __init__(self, username, password, **kwargs):
        if type(username) != str or type(password) != str:
            raise ValueError, "username and password must be strings."

        self.username = username
        self.password = password
        self.secure_repr = False

        self_dict = self.__dict__

        for option, option_type in self._valid_options:
            if option not in kwargs:
                self_dict[option] = None
                continue

            value = kwargs[option]

            if not isinstance(value, option_type):
                raise TypeError('%r must be %r' %
                    ( option, option_type ))

            self_dict[option] = value




    def send_sms(self, recipients, message, **options):
        """
        Send a message to multiple recipients.

        <recipients> is a list of telephone numbers to transmit the message to,
        format: CCNNNN where CC is the country code and NNNN is the telephone
        number, with leading zeros stripped.

        <message> is the text message in the character set specified by <dca>.
        Other optional fields are described in the class documentation.
        """

        self._phonebook_expand(recipients)

        data = {
            'msisdn': ','.join(recipients),
            'message': message
        }

        self._apply_options(data, options)
        self._test_message_length(message, options)

        lines = self._http_request('send_sms', data, options)
        code, desc, msg_id = self._parse_status(lines)
        self._raise_status(code, desc)

        return int(msg_id)




    def quote_sms(self, recipients, message, **options):
        """
        Return a floating point number indicating the number of credits that
        would be used to send a message. All parameters are, and should be
        identical to those used in send_sms.
        """

        self._phonebook_expand(recipients)

        data = {
            'msisdn':  ','.join(recipients),
            'message': message
        }

        self._apply_options(data, options)
        self._test_message_length(message, options)

        lines = self._http_request('quote_sms', data, options)
        code, desc, return_value = self._parse_status(lines)
        self._raise_status(code, desc)

        return float(return_value)




    def get_credits(self, **options):
        """
        Return a floating point number indicating the amount of credit remaining
        on this BulkSMS.co.uk account.
        """

        data = {}

        self._apply_options(data, options, self._bare_request)
        lines = self._http_request('get_credits', data, options)
        code, desc, return_value = self._parse_status(lines)
        self._raise_status(code, desc)

        return float(return_value)




    def get_report(self, msg_id, recipient = None, **options):
        """
        Returns a list of (<recipient>, <status_code>, <description>) triples for
        the given <msg_id>. If <recipient> is specified, return a list of one
        triple for the given recipient.
        """

        recipient = self._phonebook_expand_string(recipient)

        data = { 'msg_id': msg_id }

        if recipient != None:
            data['msisdn'] = recipient

        self._apply_options(data, options, self._bare_request)
        lines = self._http_request('get_report', data, options)
        code, desc, return_value = self._parse_status(lines)
        self._raise_status(code, desc)


        triples = []

        for line in lines:
            parts = line.split('|')
            triples.append((parts[0], int(parts[1]), parts[2]))


        return triples



    def poll_report(self, msg_id, report_fn, recipient = None, **options):
        """
        Periodically ask BulkSMS for a delivery report for the given
        <msg_id>. If <recipient> is given, then only ask for the status
        of that recipient.

        When the status changes, hand <report_fn> the list returned by
        get_report(). All arguments, with the exception of <report_fn>,
        are identical to get_report().
        """

        poll_time = self.poll_time or (5 * 60)
        poll_wait = self.poll_wait or 10

        result = None

        while poll_time > 0:
            last_result = result
            result = self.get_report(msg_id, recipient, **options)

            all_done = True

            for item in result:
                if item[1] != 11:
                    all_done = False

            if last_result != result:
                report_fn(result)

            if all_done:
                return

            poll_time -= poll_wait
            time.sleep(poll_wait)




    def _test_message_length(self, message, options):
        """
        Check the given messages do not exceed the given limits for their data
        coding alphabet.
        """

        dca = options.get('dca', '7bit')
        length = len(message)

        if length <= self._max_lengths[dca]:
            return


        raise MessageLengthException(length, self._max_lengths[dca])




    def _parse_status(self, lines):
        """
        Remove the status line from <lines>, and return a
        (<code>, <description>, <return_value>)
        """

        code = None
        description = None
        return_value = None

        status = lines.pop(0).split('|')

        if len(status) == 1:
            return None, None, status[0]

        if len(status) == 3:
            return_value = status[2]
        else:
            return_value = None

        code = int(status[0])
        description = status[1]

        return code, description, return_value




    def _raise_status(self, code, description):
        '''
        Raise an error if the <code> indicates failure.
        '''

        ok_codes = ( None, 0, 10, 11, 12, )

        if code in ok_codes:
            return

        if   code == 22:
            raise InternalFatalError
        if   code == 23:
            raise AuthenticationException(description)
        elif code == 24:
            raise DataValidationException(description)
        elif code == 25 or code == 26:
            raise InsufficientCreditsException
        elif code == 27 or code == 28:
            raise QuotaException(code, description)
        elif code == 50:
            raise DuplicateMessageException
        elif code == 1001:
            raise MessageNotFoundException
        elif code != 1000:
            raise UnknownException(code, description)




    def _apply_options(self, data_dict, user_options, applicable = None):
        """
        Update <data_dict> to include the options from <options>, and any
        configured for this class instance.
        """

        applicable_options = (
            'username', 'password', 'sender', 'msg_class',
            'dca', 'want_report', 'cost_route', 'nodup',
            'repliable'
        )

        if applicable is not None:
            applicable_options = applicable


        for option in applicable_options:
            if option in user_options and user_options[option] != None:
                data_dict[option] = self._convert(user_options[option])
            elif option in self.__dict__ and self.__dict__[option] != None:
                data_dict[option] = self._convert(self.__dict__[option])

        if 'msg_id' in user_options:
            data_dict['msg_id'] = str(user_options['msg_id'])




    def _convert(self, value):
        '''
        Convert basic Python types into a format understood by BulkSMS.
        '''

        if type(value) is bool:
            if value:
                return '1'
            else:
                return '0'

        return str(value)




    def __repr__(self):
        if self.secure_repr:
            return '<instance of BulkSMS.BulkSMS with id %d>' % id(self)

        used_options = [ ]

        for option, option_type in self._valid_options:
            this_option = vars(self)[option]

            if this_option != None:
                used_options.append('%s=%r' % (option, this_option))

        if len(used_options):
            used_opts_str = ', ' + ', '.join(used_options)
        else:
            used_opts_str = ''

        return 'BulkSMS(%r, %r%s)' % \
            ( self.username, self.password, used_opts_str)




    def _phonebook_expand(self, list):
        if self.phonebook == None:
            return

        for keyword_idx in range(len(list)):
            keyword = list[keyword_idx]
            result = self.phonebook.lookup_keyword(keyword)

            if len(result):
                list[keyword_idx] = result.pop(0)
                list.extend(result)




    def _phonebook_expand_string(self, string):
        if self.phonebook == None:
            return string

        result = self.phonebook.lookup_keyword(string)
        return result or string




    def _http_single(self, url, data):
        '''
        Make a single (non-retryable) HTTP request.
        '''

        try:
            return urllib2.urlopen(url, data)

        except urllib2.HTTPError, error:
            raise CommunicationException('HTTP server: %s' % error)

        except urllib2.URLError, error:
            raise CommunicationException(str(error.reason[1]))




    def _http_retry(url, data, wait, retries):
        '''
        Attempt to request an HTTP url multiple times.
        '''

        while retries:
            retries -= 1

            try:
                return urllib2.urlopen(url, data)

            except urllib2.HTTPError, error:
                time.sleep(wait)
                continue

            except urllib2.URLError, error:
                raise CommunicationException(str(error.reason))




    def _http_request(self, request, data, options):
        """
        Make an HTTP request to BulkSMS.co.uk.
        """

        port, path = self._ports_paths[request]

        wait = options.get('transient_wait', self.transient_wait)
        retries = options.get('transient_retries', self.transient_retries)
        data_encoded = urllib.urlencode(data)

        url = 'http://%s:%d%s' % ( self._server, port, path )


        if wait is None or retries is None:
            response = self._http_single(url, data_encoded)

        else:
            response = self._http_retry(url, data_encoded, wait, retries)


        return response.read().split('\n')
