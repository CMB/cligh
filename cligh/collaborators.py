#!/usr/bin/python
# Commands for managing collaborators.

from cligh.utils import get_repository_name, remove_username

def cmd_collab_add(client, args):
	"""Add a collaborator to a repo."""
	repository = get_repository_name(args.repository)
	repository = remove_username(repository)
	print client.repos.add_collaborator(repository, args.user)

def cmd_collab_remove(client, args):
	"""Remove a collaborator from a repo."""
	repository = get_repository_name(args.repository)
	repository = remove_username(repository)
	print client.repos.remove_collaborator(repository, args.user)

def cmd_collab_list(client, args):
	"""List a repository's collaborators."""
	repository = get_repository_name(args.repository)
	collaborators = client.repos.list_collaborators(repository)
	if not collaborators:
		print 'There are no collaborators for %s.' % repository
	else:
		print 'The following people are collaborating on %s:' % \
			repository
		for collaborator in collaborators:
			print collaborator

def make_collab_parser(subparsers):
	collab = subparsers.add_parser('collab', help='Manage collaborators.')
	subparsers = collab.add_subparsers(title='Collaborator-related Subcommands')
	collab_list = subparsers.add_parser('list', help='List collaborators for a given repository.')
	collab_list.set_defaults(func=cmd_collab_list)
	collab_list.add_argument('--repository', help='Name of the repository.')
	collab_add = subparsers.add_parser('add', help='Add a collaborator to a repository.')
	collab_add.set_defaults(func=cmd_collab_add)
	collab_add.add_argument('user', help='Name of the user.')
	collab_add.add_argument('--repository', help='Name of the repository.')
	collab_remove = subparsers.add_parser('remove', help='Remove a collaborator from a repository.')
	collab_remove.set_defaults(func=cmd_collab_remove)
	collab_remove.add_argument('user', help='Name of the user.')
	collab_remove.add_argument('--repository', help='Name of the repository.')
