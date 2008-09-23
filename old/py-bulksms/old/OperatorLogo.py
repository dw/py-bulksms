
"""
OperatorLogo.py: Classes and utilities for working with Nokia Operator Logos.
"""

__author__ = 'David Wilson'

import os, array





class InformationElement:
	"""
	Class representing the IE from the SMS user data header.
	"""



class UserDataHeader:
	"""
	Class representing the SMS user data header.
	"""

	length = 0x0
	IEI    = 0x0000
	

	def make_packet(self):
		"""
		Return the encoded user data header suitable for use with 8bit data
		coding alphabet.
		"""

		

class OperatorLogo:
	"""
	Class representing an operator logo file.
	"""

	def __init__(self, filename = None, width = None, height = None):
		if filename != None:
			self.load_nol_file(filename)
			return

		else:
			if width == None or height == None:
				raise ValueError("filename unset and dimensions were unspecified.")

			self.width = width
			self.height = height
			self.blank_logo()




	def blank_logo(self):
		"""
		Reinitialise this class instance with empty data.
		"""

		self.rows = []

		for row in range(self.height):
			self.rows.append(array.array('I'))

			for column in range(self.width):
				self.rows[row].append(0)

