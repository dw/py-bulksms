#!/usr/bin/env python2.3

'''
index.py: Example of using the callback interface.
'''

from BulkSMS import ReplyHandler




print "Content-type: text/plain"

f = open('/tmp/bulksms_reply_callback', 'w')
f.write(repr(ReplyHandler.fetch_reply()))

print 1
