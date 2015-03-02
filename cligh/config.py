import configparser
import getpass
import os
from github import Github
from xdg import BaseDirectory
from . import utils

USERNAME = None
TOKEN = None

def get_username():
	global USERNAME
	return USERNAME

def get_token():
	global TOKEN
	return TOKEN

def get_config_dir():
	"""Return the name of the directory containing the application's config file."""
	config_dir = BaseDirectory.load_first_config('cligh')
	if config_dir is None:
		config_dir = BaseDirectory.save_config_path('cligh')
	return config_dir

def get_config_filename():
	"""Get the absolute pathname of the config file."""
	config_dir = get_config_dir()
	return os.path.join(config_dir, 'cligh.conf')

def read_config_file():
	global USERNAME, TOKEN
	config_parser = configparser.ConfigParser()
	config_filename = get_config_filename()
	try:
		with open(config_filename, 'r') as f:
			config_parser.readfp(f)
	except configparser.Error as e:
		utils.die("""The following error was encountered while attempting to parse the configuration file.
%s
This may indicate a mal-formed configuration file.
Recreate the file by invoking
cligh configure
""" % str(e))
	except IOError as e:
		utils.die("""The following error occurred while trying to open the configuration file.
%s.
If you have not already done so, create the configuration file using
cligh configure
at your shell prompt.
""" % str(e))

	try:
		USERNAME = config_parser.get('credentials', 'username')
		TOKEN = config_parser.get('credentials', 'token')
	except configparser.Error as e:
		utils.die("""The config file is missing one or more expected options.
You should probably recreate it using these two commands:
rm %s
cligh configure
""" % config_filename)

def do_configcmd():
	"""Create an oauth token.  Write the username and token to the config
file.  Should be called the first time the application is executed."""
	dummy_validator = lambda x : True
	username = utils.read_user_input('Username', dummy_validator)
	password = getpass.getpass('Password:')
	client = Github(username, password)
	user = client.get_user()
	authorization = user.create_authorization(scopes=['user', 'repo', 'gist', 'delete_repo'], note='cligh', note_url='https://github.com/CMB/cligh')
	config_parser = configparser.ConfigParser()
	config_parser.add_section('credentials')
	config_parser.set('credentials', 'username', username)
	config_parser.set('credentials', 'token', authorization.token)
	os.umask(0o77) # Want permissions of 0600.
	with open(get_config_filename(), 'w') as f:
		config_parser.write(f)
	print('cligh configured and authorized for use with github.')

def make_configcmd_parser(subparsers):
	configcmd = subparsers.add_parser('configure', help='Configure cligh.')
	configcmd.set_defaults(func=do_configcmd)
