# Repository-related commands.

from cligh.utils import get_working_repo, read_user_input, die
from github import GithubException

def create(client, args):
	"""Create a new repository."""

	def validate_description(text):
		if len(text) == 0:
			print('Description may not be empty.  Try again.')
			return False
		return True

	def validate_name(text):
		if len(text) == 0:
			print('Name may not be empty.  Try again.')
			return False
		if any(char for char in text if char.isspace()):
			print('Name may not contain spaces.  Try again.')
			return False
		# What other characters don't belong in the name?
		return True

	def validate_homepage(text):
		# This is a lame excuse for validation.
		if len(text) == 0:
			print('Home page may not be empty.  Try again.')
			return False
		return True

	name = read_user_input('Repository name', validate_name)
	homepage = read_user_input('Homepage', validate_homepage)
	description = read_user_input('Description', validate_description)
	print(client.get_user().create_repo(name=name, description=description, homepage=homepage))

def fork(client, args):
	"""Fork a repository."""
	repo_to_fork = get_working_repo(client, args.repository)
	client.get_user().create_fork(repo_to_fork)
	print('Repository forked.')

def do_list(client, args):
	"""Command to list the repos for a given user."""
	user = client.get_user(args.user)
	repos = user.get_repos()
	print('%s has the following repositories:' % args.user)
	print('Name - Description')
	for repo in repos:
		print('%s - %s' % (repo.name, repo.description))

def addlabel(client, args):
	# xxx Make this configurable by the user.  White is a sane
	# default, for now.
	color = 'ffffff'
	repository = get_working_repo(client, args.repository)
	try:
		repository.create_label(args.label, color)
	except GithubException as e:
		die('''Unable to create label %s.
The complete error response was:
%s
''' % (args.label, e.data))
	print('Label added.')

def remlabel(client, args):
	repository = get_working_repo(client, args.repository)
	try:
		label = repository.get_label(args.label)
		label.delete()
	except GithubException as e:
		die('''Unable to delete label %s from this repository.
Error message: %s
''' % (args.label, e.data['message']))
	print('Label removed.')

def make_repo_parser(subparsers):
	repo = subparsers.add_parser('repo', help='Manage and query repositories.')
	subparsers = repo.add_subparsers(title='Repository-related Subcommands')
	subparsers.required = True
	subparsers.dest = 'repo_command'
	repo_list = subparsers.add_parser('list', help='List repositories belonging to a given user.')
	repo_list.set_defaults(func=do_list)
	repo_list.add_argument('user')
	repo_create = subparsers.add_parser('create', help='Create a new repository.')
	repo_create.set_defaults(func=create)
	repo_fork = subparsers.add_parser('fork', help='Fork an existing repository.')
	repo_fork.set_defaults(func=fork)
	repo_fork.add_argument('repository', help='Name of the repository, in the form USERNAME/REPONAME')
	repo_addlabel = subparsers.add_parser('add_label', help='Add a label to a repository.')
	repo_addlabel.set_defaults(func=addlabel)
	repo_addlabel.add_argument('--repository', help='Name of the repository, in the form USERNAME/REPONAME')
	repo_addlabel.add_argument('label', help='Name of the label to add')
	repo_remlabel = subparsers.add_parser('remove_label', help='Remove a label from a repository.')
	repo_remlabel.set_defaults(func=remlabel)
	repo_remlabel.add_argument('--repository', help='Name of the repository, in the form USERNAME/REPONAME')
	repo_remlabel.add_argument('label', help='Name of the label to remove')
