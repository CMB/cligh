# Commands for managing collaborators.

from . import utils

def add(client, args):
	"""Add a collaborator to a repo."""
	repository = utils.get_working_repo(client, args.repository)
	collaborator = utils.get_named_user(client, args.user)
	repository.add_to_collaborators(collaborator)
	print('Collaborator added.')

def remove(client, args):
	"""Remove a collaborator from a repo."""
	repository = utils.get_working_repo(client, args.repository)
	collaborator = utils.get_named_user(client, args.user)
	repository.remove_from_collaborators(collaborator)
	print('Collaborator removed.')

def do_list(client, args):
	"""List a repository's collaborators."""
	repository = utils.get_working_repo(client, args.repository)
	collaborators = repository.get_collaborators()
	if not collaborators:
		print('There are no collaborators for %s.' % repository.full_name)
	else:
		print('The following people are collaborating on %s:' % \
			repository.full_name)
		for collaborator in collaborators:
			print(collaborator.login)

def make_collab_parser(subparsers):
	collab = subparsers.add_parser('collab', help='Manage collaborators.')
	subparsers = collab.add_subparsers(title='Collaborator-related Subcommands')
	subparsers.required = True
	subparsers.dest = 'collab_command'
	collab_list = subparsers.add_parser('list', help='List collaborators for a given repository.')
	collab_list.set_defaults(func=do_list)
	collab_list.add_argument('--repository', help='Name of the repository.')
	collab_add = subparsers.add_parser('add', help='Add a collaborator to a repository.')
	collab_add.set_defaults(func=add)
	collab_add.add_argument('user', help='Name of the user.')
	collab_add.add_argument('--repository', help='Name of the repository.')
	collab_remove = subparsers.add_parser('remove', help='Remove a collaborator from a repository.')
	collab_remove.set_defaults(func=remove)
	collab_remove.add_argument('user', help='Name of the user.')
	collab_remove.add_argument('--repository', help='Name of the repository.')
