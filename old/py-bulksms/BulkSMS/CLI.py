"""
BulkSMS/CLI.py: Command-line wrapper around BulkSMS.
Author: David M. Wilson <dw-BulkSMS_CLI.py@botanicus.net>.
"""

import getopt, os, time, sys
import BulkSMS, BulkSMS.PhoneBook



def usage(argv0):
	"""
	Print command-line program usage.
	"""

	print __doc__
	print argv0, "send    <opts> <msg> <phone1> [phone2 ..]"
	print argv0, "quote   <opts> <msg> <phone1> [phone2 ..]"
	print argv0, "report  <opts> <msg_id> [phone1]"
	print argv0, "poll    <opts> <msg_id> [phone1]"
	print argv0, "credits <opts>"
	print
	print "Options:"
	print "   --sender=<sender>        Sender field."
	print "   --flash                  Send as flash message."
	print "   --dca=<7bit|8bit|16bit>  Data coding alphabet."
	print "   --report                 Request delivery report."
	print "   --cost_route=<1|2|3>     Message route."
	print "   --nodup                  Suppress duplicate messages."
	print "   --wait=<integer>         Seconds to wait between failures."
	print "   --retry=<integer>        Number of attempts before failing."
	print "   --username=<string>      Username to connect using."
	print "   --password=<string>      Password to connect using."
	print "   --poll                   After sending immediately start poll."
	print "   --repliable              Initiate a 2-way SMS."
	print
	print "   send  sends a message,"
	print "  quote  retrieves the cost for sending a message,"
	print " report  retrieves a delivery report,"
	print "   poll  Displays message status until delivered, and"
	print "credits  retrieves the total credits on your account."
	print
	print "A simple '<keyword>: <phone1>, <phone2>, <phone3><nl>' format"
	print "shortcut database is stored in your homedir/.sms_phonebook."
	print



def format_status_report(triple):
	"""
	Return a string containing a formatted version of the given <triple>. The
	<triple> is one returned in the list from BulkSMS.get_report().
	"""

	return "%-14s %2s %s" % triple




class _FileReporter(object):
	def __init__(self, output):
		assert isinstance(output, file)
		self.output = output

	def report(self, result):
		for triple in result:
			print >> self.output, format_status_report(triple)




def poll_report_text(server, msg_id, recipient = None, output = sys.stdout):
	"""
	Call poll_report in such a way as to print status reports to the given
	file object <output>.
	"""

	server.poll_report(msg_id, _FileReporter(output).report, recipient)




def command_line(argv):
	"""
	Act as a command-line tool.
	"""

	long_options = [
		'sender=', 'flash', 'dca=', 'report', 'cost_route=', 'nodup',
		'wait=', 'retry=', 'username=', 'password=', 'poll',
		'repliable', 'file=',
	]


	if len(argv) < 2:
		usage(argv[0])
		return 1

	options, arguments = getopt.gnu_getopt(argv[1:], "", long_options)

	if len(arguments) > 0:
		mode = arguments[0]
		arguments.pop(0)

	else:
		mode = None


	command_args = {}
	input_file = None

	command_args['sender'] = os.environ.get('BULKSMS_SENDER', None)
	command_args['repliable'] = 'BULKSMS_REPLIABLE' in os.environ
	command_args['want_report'] = 'BULKSMS_REPORT' in os.environ

	username = os.environ.get('BULKSMS_USERNAME', None)
	password = os.environ.get('BULKSMS_PASSWORD', None)
	poll = 'BULKSMS_POLL' in os.environ

	for option, argument in options:
		if option == "--sender":
			command_args['sender'] = argument

		elif option == "--flash":
			command_args['msg_class'] = 0

		elif option == "--dca":
			command_args['dca'] = argument

		elif option == "--report":
			command_args['want_report'] = 1

		elif option == "--cost_route":
			command_args['cost_route'] = argument

		elif option == "--nodup":
			command_args['nodup'] = 1

		elif option == "--wait":
			command_args['transient_wait'] = argument

		elif option == "--retry":
			command_args['transient_retries'] = argument

		elif option == "--username":
			username = argument

		elif option == "--password":
			password = argument

		elif option == "--mode":
			mode = argument

		elif option == "--poll":
			command_args['want_report'] = True
			poll = True

		elif option == "--repliable":
			command_args['repliable'] = True

		elif option == "--file":
			if argument == '-':
				input_file = sys.stdin
			else:
				input_file = open(argument)


	if  command_args.get('repliable', False) and 'sender' in command_args:
		del command_args['sender']

	if mode not in ( "send", "quote", "credits", "report", "poll" ):
		print "!!! Please specify a valid mode."
		return 1

	if not username or not password:
		print "!!! Please specify a username and password."
		return 1



	server = BulkSMS.BulkSMS(username, password)
	server.phonebook = BulkSMS.PhoneBook.HomedirPhoneBook()

	if mode == 'send' or mode == 'quote':
		if input_file is not None:
			if input_file is sys.stdin:
				print "Enter your message followed by EOL> ",
				sys.stdout.flush()
				message = input_file.read()
				print
			else:
				message = input_file.read()
		else:
			message = arguments.pop(0)

		recipients = arguments

		if len(recipients) < 1:
			print "!!! Please specify your message and at least one recipient."
			return 1

		if mode == 'quote':
			cost = server.quote_sms(recipients, message, **command_args)
			print "Message cost:", BulkSMS.format_credits(cost), "credits."

		else:
			msg_id = server.send_sms(recipients, message, **command_args)
			print "Message sent. Message ID:", msg_id

			if poll:
				poll_report_text(server, msg_id)

		return 0


	if mode == 'credits':
		print "Credits available:", BulkSMS.format_credits(server.get_credits())
		return 0


	if mode == 'report' or mode == 'poll':
		if len(arguments) < 1 or len(arguments) > 2:
			print "!!! Please specify a <msg_id> and optionally a recipient."
			return 0

		msg_id = arguments.pop(0)

		if len(arguments):
			recipient = arguments.pop(0)

		else:
			recipient = None


		if mode == 'poll':
			poll_report_text(server, msg_id, recipient)

		report = server.get_report(msg_id, recipient)

		for triple in report:
			print format_status_report(triple)

		print
