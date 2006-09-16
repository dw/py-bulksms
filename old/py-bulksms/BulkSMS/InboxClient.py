
'''
BulkSMS/InboxClient.py: 2-way SMS server inbox client.
Author: David M. Wilson <dw-InboxServer.py@botanicus.net>.
'''

import urllib2, socket
from CoreBulkSMS import BulkSMSException



class AuthenticationException(BulkSMSException):
    '''
    Exception. Raised when the Inbox server refuses our (<username>,
    <password>).
    '''

    def __str__(self):
        return 'Authentication failure.'





class InboxClient:
    '''
    Client class for accessing a BulkSMS 2-way proxy server.
    '''

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.session_up = False


    def create_tcp_session(self, session_addr = None ):
        '''
        Authenticate with the server, get a session cookie, and connect
        to the session proxy via TCP.
        '''

        fields = {}

        if session_addr is not None:
            session_ip = session_addr[0]

            if session_addr[1] is not None:
                session_ip += ':' + str(session_addr[1])

            fields['session_ip'] = session_ip


        # Get our cookie, IP address, and port number.

        lines = self._do_request('create-tcp-session',
            fields, http = True)

        code, desc, return_value = self._parse_status(lines)
        self._raise_status(code, desc)

        result = lines.pop(0).split('|')
        cookie = result[0]
        server_addr = ( result[1], int(result[2]) )


        # Connect to the server.

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if session_addr is not None:
            sock.bind(session_addr)

        sock.settimeout(30)
        sock.connect(server_addr)

        sock_file = sock.makefile('r+')
        sock_file.write(cookie + '\n')

        code, desc = sock_file.readline().split('|')
        self._raise_status(code, desc)

        self.session_up = True
        self.session_sock = sock
        self.session_file = sock_file


    def destroy_tcp_session(self):
        if self.session_up == False:
            return

        self.session_file.close()
        self.session_sock.close()
        self.session_file = None
        self.session_sock = None
        self.session_up = False


    def list_unread(self):
        lines = self._do_request('list-unread', {})
        code, desc, return_value = self._parse_status(lines)
        self._raise_status(code, desc)

        output = []

        for msisdn, sender, message, msg_id, referring_msg_id in something:
            output.append((
                msisdn, sender,
                int(msg_id), int(referring_msg_id)
            ))


        return output


    def _parse_status(self, lines):
        '''
        Remove the status line from <lines>, and return a
        (<code>, <description>, <return_value>)
        '''

        status = lines.pop(0).split('|')
        return_value = None

        code = int(status[0])
        description = status[1]

        if len(status) == 3:
            return_value = status[2]

        return code, description, return_value


    def _do_http(self, req_dict):
        req_dict['username'] = self.username
        req_dict['password'] = self.password

        data_encoded = urllib2.urlencode(data)
        response = urllib2.urlopen(self.url, data_encoded)

        return response.read().split('\n')


    def _do_session(self, req_dict):
        self.session_file.write(urllib.urlencode(fields) + '\n')
        response = []

        while 1:
            line = self.session_file.readline()
            if line == '\n':
                break

            response.append(line[:-1])

        return response


    def _do_request(self, request, fields, http = None):
        '''
        Make a request to the server.
        '''

        req_dict = { 'request': request }
        req_dict.update(fields)


        if self.session_up == False or http == True:
            return self._do_http(request, req_dict)

        return self._do_session(request, req_dict)
