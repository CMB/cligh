#!/usr/bin/python
"""Commands for managing and querying issues."""

from cligh.utils import text_from_editor, get_repository_name

# A helper function.
def print_enclosed_text(text):
	"""Print some text, enclosed by horizontal lines."""
	print '-' * 80
	print text
	print '-' * 80
	print

def print_comment(comment):
	print 'Comment by %s on %s at %s' % (comment.user,
		comment.created_at.date(),
		comment.created_at.strftime('%H:%M:%S'))
	print_enclosed_text(comment.body)

def do_open(client, args):
	"""Create a new issue."""
	repository = get_repository_name(args.repository)
	print 'Please enter the long description for this issue.'
	print 'Starting your text editor:'
	desc_text = text_from_editor()
	print client.issues.open(repository, args.title, desc_text)

def close(client, args):
	"""Close an existing open issue."""
	repository = get_repository_name(args.repository)
	print client.issues.close(repository, args.number)

def do_list(client, args):
	"""Command to list the issues for a given repository."""
	repository = get_repository_name(args.repository)
	status = args.status or 'open'
	issues = client.issues.list(repository, state=status)
	if not issues:
		print '%s has no %s issues' % (repository, status)
	else:
		print '%s has the following %s issues' % (repository, status)
		print 'Issue# - Title'
	for issue in issues:
		print '%s - %s' % (issue.number, issue.title)

def get(client, args):
	repository = get_repository_name(args.repository)
	try:
		issue = client.issues.show(repository, args.number)
		comments = client.issues.comments(repository, args.number)
	except:
		die(
"""Unable to retrieve the issue because of the following error:
%s: %s
""" % (sys.exc_info()[0], sys.exc_info()[1]))
	print 'Issue #%d: %s' % (issue.number, issue.title)
	print 'Opened by %s on %s at %s' % (issue.user, issue.created_at.date(),
		issue.created_at.strftime('%H:%M:%S'))
	print 'Last updated on %s at %s' % (issue.updated_at.date(),
		issue.updated_at.strftime('%H:%M:%S'))
	if issue.labels:
		print 'Labels:'
		for label in issue.labels:
			print '* %s' % label
	print 'Long description:'
	print_enclosed_text(issue.body)
	if comments:
		for comment in comments:
			print_comment(comment)

def comment(client, args):
	repository = get_repository_name(args.repository)
	print 'Starting your text editor, so that you can compose your comment:'
	comment_text = text_from_editor()
	print client.issues.comment(repository, args.number, comment_text)

def addlabel(client, args):
	repository = get_repository_name(args.repository)
	print client.issues.add_label(repository, args.number, args.label)

def remlabel(client, args):
	repository = get_repository_name(args.repository)
	print client.issues.remove_label(repository, args.number, args.label)

def make_issue_parser(subparsers):
	issue = subparsers.add_parser('issue', help='Manage and query issues.')
	subparsers = issue.add_subparsers(title='Issue-related subcommands.')

	issue_list = subparsers.add_parser('list', help='List issues for a given repository.')
	issue_list.set_defaults(func=do_list)
	issue_list.add_argument('--status',
		help='List issues having this status; default is "open"')
	issue_list.add_argument('--repository', help='Name of the repository.')

	issue_get = subparsers.add_parser('get', help='View an issue.')
	issue_get.set_defaults(func=get)
	issue_get.add_argument('number', help='Number of the issue to retrieve.')
	issue_get.add_argument('--repository', help='Name of the repository.')

	issue_close = subparsers.add_parser('close', help='Close an issue.')
	issue_close.set_defaults(func=close)
	issue_close.add_argument('number',
		help='Number of the issue to close.')
	issue_close.add_argument('--repository', help='Name of the repository.')

	issue_open = subparsers.add_parser('open', help='Open a new issue.')
	issue_open.set_defaults(func=do_open)
	issue_open.add_argument('title', help='Title of the issue.')
	issue_open.add_argument('--repository', help='Name of the repository.')

	issue_comment = subparsers.add_parser('comment',
		help='Comment on an existing issue.')
	issue_comment.set_defaults(func=comment)
	issue_comment.add_argument('number',
		help='Number of the issue on which you wish to comment.')
	issue_comment.add_argument('--repository', help='Name of the repository.')

	issue_addlabel = subparsers.add_parser('add_label',
		help='Add a label to an issue.')
	issue_addlabel.set_defaults(func=addlabel)
	issue_addlabel.add_argument('number',
		help='Number of the issue on which you wish to add a label.')
	issue_addlabel.add_argument('label', help='Label to add.')
	issue_addlabel.add_argument('--repository', help='Name of the repository.')

	issue_remlabel = subparsers.add_parser('remove_label',
		help='Remove a label from an issue.')
	issue_remlabel.set_defaults(func=remlabel)
	issue_remlabel.add_argument('number',
		help='Number of the issue from which you wish to remove a label.')
	issue_remlabel.add_argument('label', help='Label to remove.')
	issue_remlabel.add_argument('--repository', help='Name of the repository.')

