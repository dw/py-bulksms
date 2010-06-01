
# py-BulkSMS GNU Make wrapper.
# $Id$

VERSION=0.1
LOCAL_PATH=/usr/local/BulkSMS-$(VERSION)

all:
	@echo
	@echo "You probably want 'make local_install'. Available targets:"
	@echo
	@echo "   make distutils_install     Use distutils installer."
	@echo "   make local_install         Install to '$(LOCAL_PATH)'."
	@echo "   make local_uninstall       Uninstall from '$(LOCAL_PATH)'."
	@echo


distutils_install:
	python setup.py install

local_install:
	cp -r . $(LOCAL_PATH)
	ln -fs $(LOCAL_PATH)/sms /usr/local/bin/sms

local_uninstall:
	rm -rf $(LOCAL_PATH) /usr/local/bin/sms
