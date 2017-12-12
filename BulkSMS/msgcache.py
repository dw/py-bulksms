"""
BulkSMS/msgcache.py: Client-side message cache.
"""

__author__ = 'David Wilson'

import os, time, sys, pickle
from BulkSMS import BulkSMSException


class CacheException(BulkSMSException):
    pass


class NotFound(CacheException):
    pass


class AlreadyExists(CacheException):
    pass


class MessageCache(object):
    """
    Cilent-side message cache implementation.
    """

    def __init__(self, path, umask = 0o700):
        self.path = path
        if not os.path.exists(path):
            os.mkdir(path, umask)

    def last_id(self):
        last_pathname = os.path.join(self.path, 'last')
        if os.path.exists(last_pathname):
            return int(os.path.basename(os.readlink(last_pathname)))

    def exists(self, msg_id):
        pathname = os.path.join(self.path, str(msg_id))
        return os.path.exists(pathname)

    def purge(self):
        path = self.path
        for filename in os.listdir(path):
            os.unlink(os.path.join(path, filename))

    def list(self):
        str_ids = os.listdir(self.path)
        last_idx = str_ids.find('last')
        if last_idx != -1:
            str_ids.pop(last_idx)

        return list(map(int, str_ids))

    def put(self, msg):
        pathname = os.path.join(self.path, str(msg.msg_id))
        if os.path.exists(pathname):
            raise AlreadyExists()

        fp = file(pathname, 'w')
        fp.write(pickle.dumps(msg))
        fp.close()

        last_pathname = os.path.join(self.path, 'last')
        if os.path.exists(last_pathname):
            os.unlink(last_pathname)

        os.symlink(pathname, last_pathname)

    def remove(self, msg):
        pathname = os.path.join(self.path, str(msg.msg_id))
        if not os.path.exists(pathname):
            raise NotFound()

        os.unlink(pathname)

    def get(self, msg_id):
        pathname = os.path.join(self.path, str(msg_id))
        return pickle.loads(file(pathname))
