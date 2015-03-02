import locale
import os
import os.path
import re
import subprocess
import sys
import tempfile

# Helper functions.
def print_error(message):
	"""Display an error message."""
	if not message.endswith('\n'):
		message += '\n'
	sys.stderr.write(message)

def die(message):
	"""Terminate, displaying an error message."""
	print_error(message)
	sys.exit(1)

def read_git_config(key):
	"""Read a value from git's configuration files."""
	cmd = ['git', 'config']
	cmd.append(key)
	output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()
	encoding = locale.getpreferredencoding(False)
	return output[0].strip().decode(encoding)

def read_user_input(prompt, validator_func):
	"""Read and validate user input."""
	user_text = ''
	valid_input = False
	while not valid_input:
		sys.stdout.write('%s: ' % prompt)
		sys.stdout.flush()
		user_text = sys.stdin.readline()
		if not user_text:
			die('Could not read input from the user; unable to proceed.')
		user_text = user_text[0:-1] # Snip off the newline.
		if validator_func(user_text):
			valid_input = True
	return user_text

def get_repository_name(name):
	"""Get the name of the repository to work on.
Either we return the "name" argument (if it is a non-empty string), or
we try to detect the repository's name by looking at remote.origin.url."""

	if not name:
		name = read_git_config('remote.origin.url')
		match = re.match(r'''(?x)
			(?:git@github.com:     # ssh
			|https://github.com/)  # https
			(.+)                   # user/repo
			(?:\.git               # optional extension
			|(?<!\.git))           # anything but extension
			$''', name)
		if not match:
			die(
"""This command expects a repository name, but the name is unknown.
There are two ways to indicate a repository.
First, you can supply the --repository argument on the command line.
If no --repository argument is specified, and the current directory is
within a clone of a project hosted on github, then the name of the repository
is detected automatically.  In order for this auto-detection to work,
the remote named "origin" must point to github.
""")

		name = match.group(1)
	return name

def split_repo_name(repository):
	"""Take a string of the form user/repo, and return the tuple
(user, repo).  If the string does not contain the username, then just
return None for the user."""
	nameparts = repository.split('/', 1)
	if len(nameparts) == 1:
		return (None, nameparts[0])
	else:
		return (nameparts[0], nameparts[1])

def get_working_repo(client, full_reponame):
	full_reponame = get_repository_name(full_reponame)
	username, reponame = split_repo_name(full_reponame)
	if username:
		user = client.get_user(username)
	else:
		user = client.get_user()
	repository = user.get_repo(reponame)
	return repository

def get_named_user(client, username):
	try:
		user = client.get_user(username)
	except GithubException as e:
		die('''Failed to retrieve the record for user %s:
Encountered the following exception:
%s
''' % (username, str(e)))
	return user

def find_executable(executable):
	path = os.environ['PATH'].split(os.pathsep)
	for subdirectory in path:
		tryname = os.path.join(subdirectory, executable)
		if os.access(tryname, os.X_OK):
			return tryname
	return None

def choose_editor():
	if 'EDITOR' in os.environ:
		editor =  os.environ['EDITOR']
	else:
		print_error('$EDITOR not set, assuming default of vi.')
		editor = find_executable('vi')
	if not editor:
		die(
"""Error: cannot continue with the current command, because the text
editor could not be found.  Please set your EDITOR environment variable
to the pathname of your preferred editor.
""")
	return editor

def text_from_editor(original_text=''):
	"""Allow a user to compose a text using his editor of choice."""
	text = ''
	editor_cmd = choose_editor()
	my_tempfile = None
	try:
		my_tempfile = tempfile.NamedTemporaryFile(delete=False, mode='w+')
		if original_text:
			my_tempfile.write(original_text)
			my_tempfile.flush()
			my_tempfile.seek(0) # And go back to the beginning.
		editor_status = subprocess.call([editor_cmd, my_tempfile.name])
		if editor_status != 0:
			die(
"""Error: the text editor did not complete successfully.  Unable to continue.
""")
		text = my_tempfile.read()
	finally:
		if my_tempfile:
			my_tempfile.close()
			os.unlink(my_tempfile.name)
	return text

