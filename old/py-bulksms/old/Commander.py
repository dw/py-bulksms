"""
BulkSMS/Commander.py: Interactive curses interface to BulkSMS.
Author: David M. Wilson <dw-BulkSMS_Commander.py@botanicus.net>.
"""

import os, time, sys
import curses, curses.textpad
import BulkSMS, BulkSMS.PhoneBook



def real_interactive(screen):
	'''
	Act as an interactive curses application. This is called from
	curses.wrapper.
	'''

	screen.erase()

	t = curses.textpad.Textbox(screen)
	res = t.edit()

	screen.erase()
	screen.addstr(0, 0, "TESTING!\r\n", curses.A_REVERSE)
	screen.addstr(0, 0, "%r" % repr(curses.color_pair(1)))
	screen.refresh()

	time.sleep(1)
	return res



class Keys:
	def findkey(self, key):
		for name, value in vars(self).iteritems():
			if value == key:
				return name


	this = locals()

	for name in dir(curses):
		if name.startswith('KEY_'):
			this[name[4:]] = getattr(curses, name)

	this.update({
		'CTRL_A': 0x01, 'CTRL_B': 0x02, 'CTRL_C': 0x03,
		'CTRL_D': 0x04, 'CTRL_E': 0x05, 'CTRL_F': 0x06,
		'CTRL_G': 0x07, 'CTRL_H': 0x08, 'CTRL_I': 0x09,
		'CTRL_J': 0x0a, 'CTRL_K': 0x0b, 'CTRL_L': 0x0c,
		'CTRL_M': 0x0d, 'CTRL_N': 0x0e, 'CTRL_O': 0x0f,
		'CTRL_P': 0x10, 'CTRL_Q': 0x11, 'CTRL_R': 0x12,
		'CTRL_S': 0x13, 'CTRL_T': 0x14, 'CTRL_U': 0x15,
		'CTRL_V': 0x16, 'CTRL_W': 0x17, 'CTRL_X': 0x18,
		'CTRL_Y': 0x19, 'CTRL_Z': 0x1a 
	})

	del this


keys = Keys()



class LineInput(object):
	'''
	A line editing widget for curses. Has the same sort of goals as
	curses.textpad, except keybindings are different.
	'''

	def __init__(self, target):
		'''
		Initialise this LineInput object. <target> is a window to draw
		on to.
		'''

		self.target = target
		self.active = False
		self.X, self.Y = 0, 0
		self.bindings = dict(self._default_bindings)


	def read(self):
		while 1:
			ch = self.target.getch()
			action = self.bindings.get(ch, None)

			if action is not None:
				action(self)

			else:
				self.process_key(ch)


	def move_left(self):
		pass

	move_left = classmethod(move_left)
	move_right = move_left
	history_last = move_left
	history_next = move_left
	delete_word = move_left
	delete_line = move_left
	reverse_search = move_left
	complete = move_left

	_default_bindings = [
		( keys.LEFT,   move_left,      ),
		( keys.RIGHT,  move_right,     ),
		( keys.UP,     history_last,   ),
		( keys.DOWN,   history_next,   ),
		( keys.CTRL_W, delete_word,    ),
		( keys.CTRL_U, delete_line,    ),
		( keys.CTRL_R, reverse_search, ),
		( keys.CTRL_I, complete,       ),
	]




def interactive(argv):
	'''
	Act as an interactive curses application.
	'''

	print repr(curses.wrapper(real_interactive))
