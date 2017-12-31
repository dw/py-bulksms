
"""
Concat.py: support for concatenated messages.
"""

__author__ = 'David Wilson'

import time, array, io


def convert8to7bit(str):
    """
    Convert 8bit string to compressed 7bit string of hex values. Returns
    string.
    """

    length = len(str)
    str = str + '\0'
    dp = ''
    j = 0

    while length > 0:
        bb = ord(str[j])
        i = 7

        while i > 0 and length > 0:
            bb = bb | ord(str[j+8-i]) << i
            dp = dp + chr(0xff & bb)
            bb = bb >> 8
            length -= 1
            i -= 1

        length -= 1
        j += 8

    return dp


class LongSMS:
    def __init__(self, message = None, msgid = None):
        self.header = array.array('B', '\x05\x00\x03\x01\x00\x00\x00')
        self.header[3] = msgid or int(time.time()) % 256
        self.data = ''

        if msgid is None:
            self.msgid = int(time.time()) % 256
        else:
            self.msgid = msgid

        if message is not None:
            self.feed(message)

    def feed(self, data):
        self.data += data

    def to_8bit(self):
        output = []

        header = self.header
        data = io.StringIO(convert8to7bit(self.data))

        segment_max_len = 140 - len(header)
        data_len = len(self.data)

        segment_count = (data_len / segment_max_len) + 1
        self.header[4] = segment_count
        this_segment = 1
        offset = 0

        while this_segment <= segment_count:
            segment_data = data.read(segment_max_len)
            header[5] = this_segment

            segment = header.tostring()
            segment += segment_data

            this_segment += 1
            offset += segment_max_len
            output.append(segment.encode('hex'))

        return output
