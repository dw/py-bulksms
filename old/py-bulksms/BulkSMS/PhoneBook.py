"""
BulkSMS/PhoneBook.py: Phone book classes and interface.
Author: David M. Wilson <dw-BulkSMS_PhoneBook.py@botanicus.net>.
"""




class BasePhoneBook:
    """
    Phonebook interface definition class. The methods and properties defined
    below are required for phonebook objects.
    """

    def __init__(self):
        pass


    def lookup_keyword(self, keyword):
        """
        Return a list of numbers associated with <keyword>.
        """

        pass


    def lookup_number(self, number):
        """
        Return a keyword that contains <number>. If none found, return <number>.
        """

        pass




class HomedirPhoneBook(BasePhoneBook):
    """
    Phonebook stored in user's home directory as text.
    """

    def __init__(self):
        import os
        self.phonebook = {}

        homedir = os.getenv("HOME") \
            or os.getenv("USERPROFILE") or None

        if not homedir:
            return


        pathname = os.path.join(homedir, '.sms_phonebook')

        for line in file(pathname, "r+"):
            keyword, numbers_text = line.split(": ")
            self.phonebook[keyword] = numbers_text.strip().split(", ")




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
