#!/usr/bin/env python

from distutils.core import setup

setup(name="BulkSMS",
	version="0.2a2",
	description="BulkSMS.co.uk Python implementation.",
	author="David M. Wilson",
	author_email="dw-BulkSMS-setup.py@botanicus.net",
	license='LGPL',
	url="http://botanicus.net/dw/",
	download_url="http://botanicus.net/dw/dl/bulksms-0.2a2.tar.gz",
	packages=['BulkSMS'],
	scripts=['sms']
)
