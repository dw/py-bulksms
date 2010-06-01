'''
BulkSMS/PhoneBook.py: Phone book classes and interface.
'''

__author__ = 'David Wilson'

import os




class BasePhoneBook:
    '''
    Phonebook interface definition class. The methods and properties defined
    below are required for phonebook objects.
    '''

    def __init__(self):
        pass


    def lookup_keyword(self, keyword):
        '''
        Return a list of numbers associated with <keyword>.
        '''

        pass


    def lookup_number(self, number):
        '''
        Return a keyword that contains <number>. If none found, return <number>.
        '''

        pass




class HomedirPhoneBook(BasePhoneBook):
    '''
    Phonebook stored in user's home directory as text.
    '''

    def get_pathname(cls):
        '''
        Return the path to the phone book.
        '''

        homedir = os.getenv('HOME') \
            or os.getenv('USERPROFILE') or None

        if homedir:
            return os.path.join(homedir, '.bulksms', 'phonebook')

    get_pathname = classmethod(get_pathname)


    def __init__(self):
        self.phonebook = {}
        pathname = self.get_pathname()

        if not os.path.exists(pathname):
            return

        for line in file(pathname, 'r+'):
            keyword, numbers_text = line.split(': ')
            self.phonebook[keyword] = numbers_text.strip().split(', ')




    def __repr__(self):
        return 'BulkSMS.PhoneBook.HomedirPhoneBook()'


    def lookup_keyword(self, keyword):
        numbers = []

        if keyword not in self.phonebook:
            numbers.append(keyword)
        else:
            for keyword2 in self.phonebook[keyword]:
                if keyword2 in self.phonebook:
                    numbers.extend(self.phonebook[keyword2])
                else:
                    numbers.append(keyword2)

        return numbers
