import sublime, sublime_plugin
import sys, os, zipfile
from random import random

try:
	import Schemr.lib.plist_parser as parser
except:
	sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
	import plist_parser as parser

	# Contains various common, internal functions for Schemr.
class Schemr():
		# Returns a list of all managed schemes.  Each scheme is itself represented by a list
		# that contains, in order, (1) its pretty-printed name, (2) its path and (3) whether
		# or not it is favorited (True or False).
	def load_schemes(self):
		all_scheme_paths = []

		# Parse the scheme file for the background colour and return the luminosity
		# in order to determine if the scheme is Dark or Light. Use load_resources()
		# first for ST3 or fallback to the absolute path for ST2.
		def parse_scheme(scheme):
			try:
				xml = sublime.load_resource(scheme)
				plist = parser.parse_string(xml)
			except:
				xml = os.path.join(sublime.packages_path(), scheme.replace('Packages/', ''))
				plist = parser.parse_file(xml)

			background_colour =  plist['settings'][0]['settings']['background']
			n = eval('0x' + background_colour[1:])
			return (n>>16)&0xff, (n>>8)&0xff, n&0xff

		try: # use find_resources() first for ST3
			for scheme_resource in sublime.find_resources('*.tmTheme'):
				all_scheme_paths.append(scheme_resource)

		except: # fallback to walk() for ST2
			# Load the paths for schemes contained in zipped .sublime-package files.
			for root, dirs, files in os.walk(sublime.installed_packages_path()):
				for package in (package for package in files if package.endswith('.sublime-package')):
					zf = zipfile.ZipFile(os.path.join(sublime.installed_packages_path(), package))
					for filename in (filename for filename in zf.namelist() if filename.endswith('.tmTheme')):
						filepath = os.path.join(root, package, filename).replace(sublime.installed_packages_path(), 'Packages').replace('.sublime-package', '').replace('\\', '/')
						all_scheme_paths.append(filepath)

			# Load the paths for schemes contained in folders.
			for root, dirs, files in os.walk(sublime.packages_path()):
				for filename in (filename for filename in files if filename.endswith('.tmTheme')):
					filepath = os.path.join(root, filename).replace(sublime.packages_path(), 'Packages').replace('\\', '/')
					all_scheme_paths.append(filepath)

		favorite_scheme_paths = self.get_favorites()

		# Given the paths of all the color schemes, add in the information for
		# the pretty-printed name and whether or not it's been favorited.
		all_schemes = []
		for scheme_path in all_scheme_paths:
			pretty_name = scheme_path.split('/').pop().replace('.tmTheme', '')
			# Get the RGB value of the scheme background and convert to luminance value
			rgb = parse_scheme(scheme_path)
			luminance = (0.2126 * rgb[0]) + (0.7152 * rgb[1]) + (0.0722 * rgb[2])
			# If the luminance is above or below than a certain theshold
			# then assign a flag to the end of the name
			if luminance < 120:
				pretty_name += '   [Dark]'
			else:
				pretty_name += '   [Light]'
			favorited = scheme_path in favorite_scheme_paths
			if favorited: pretty_name += u' \N{BLACK STAR}' # Put a pretty star icon next to favorited schemes. :)
			all_schemes.append([pretty_name, scheme_path, favorited])

		all_schemes.sort()
		return all_schemes

		# Displayes the given schemes in a quick-panel, letting the user cycle through
		# them to preview them and possibly select one.  The reason that this is a method
		# here instead of a free-standing command is that the "List all schemes" and
		# "List favorite schemes" commands function exactly the same except for the
		# underlying schemes that they operate on.  This method exists to provide that
		# common listing functionality.
	def list_schemes(self, window, schemes):
		# In listing a scheme, whether or not it is favorited is never considered.
		# (The stars that appear after favorited schemes' names are added in load_schemes().)
		# Since that information is never used, it is filtered out here for convenience
		# in passing the array to window.show_quick_panel().
		color_schemes = [['Scheme: ' + scheme[0], scheme[1]] for scheme in schemes]
		the_scheme = self.get_scheme()

		# If the active scheme isn't part of the supplied pool (the schemes variable),
		# then we can't skip the selection to that point and the best we can do is
		# start from the top of the list.
		try:
			the_index = [scheme[1] for scheme in color_schemes].index(the_scheme)
		except (ValueError):
			the_index = 0

		def on_done(index):
			if index != -1:
				self.set_scheme(color_schemes[index][1])
				sublime.status_message(color_schemes[index][0])

			if index == -1:
				self.set_scheme(the_scheme)

		# Set a selection flag to detect when the panel is first opened in some
		# versions of Sublime Text. This prevents the colour scheme from 'flickering'
		# from one scheme to another as the panel jumps to the active selection
		self.user_selected = False
		def on_select(index):
			if self.user_selected == True:
				self.set_scheme(color_schemes[index][1])
			else:
				self.user_selected = True

		try: # Attempt to enable preview-on-selection (only supported by Sublime Text 3).
			window.show_quick_panel(color_schemes, on_done, 0, the_index, on_select)
		except:
			window.show_quick_panel(color_schemes, on_done)

		# Cycles the scheme in the given direction ("next", "prev" or "rand").
	def cycle_schemes(self, color_schemes, direction):
		the_scheme = Schemr.get_scheme()
		num_of_schemes = len(color_schemes)
		# Try to find the current scheme path in the available schemes otherwise
		# start from the top of the list. Useful in case the user has manually
		# saved an invalid scheme path or the current scheme file is not available.
		try:
			the_index = [scheme[1] for scheme in color_schemes].index(the_scheme)
		except (ValueError):
			the_index = 0

		if direction == 'next':
			index = the_index + 1 if the_index < num_of_schemes - 1 else 0

		if direction == 'prev':
			index = the_index - 1 if the_index > 0 else num_of_schemes - 1

		if direction == 'rand':
			index = int(random() * len(color_schemes))

		Schemr.set_scheme(color_schemes[index][1])
		sublime.status_message(color_schemes[index][0])

	def set_scheme(self, scheme):
		sublime.load_settings('Preferences.sublime-settings').set('color_scheme', scheme)
		sublime.save_settings('Preferences.sublime-settings')

	def get_scheme(self):
		return sublime.load_settings('Preferences.sublime-settings').get('color_scheme')

	def set_favorites(self, schemes):
		sublime.load_settings('SchemrFavorites.sublime-settings').set('schemr_favorites', schemes)
		sublime.save_settings('SchemrFavorites.sublime-settings')

	def get_favorites(self):
		return sublime.load_settings('SchemrFavorites.sublime-settings').get('schemr_favorites')

Schemr = Schemr()

def plugin_loaded():
	print('schemr ready')

	# Display the full list of schemes available, regardless
	# of whether or not they are favorited
class SchemrListSchemesCommand(sublime_plugin.WindowCommand):
	def run(self):
		Schemr.list_schemes(self.window, Schemr.load_schemes())

	# Display the list of schemes that have been favorited.
	# Only available if there are favorites to display
class SchemrListFavoriteSchemesCommand(sublime_plugin.WindowCommand):
	def run(self):
		Schemr.list_schemes(self.window, [scheme for scheme in Schemr.load_schemes() if scheme[2]])

	def is_enabled(self):
		return len(Schemr.get_favorites()) > 0

	# SchemrFavoriteCurrentSchemeCommand and SchemrUnfavoriteCurrentSchemeCommand
	# work in conjunction. Only one is ever available to the user at a time,
	# depending on whether or not the active scheme is already favorited.
class SchemrFavoriteCurrentSchemeCommand(sublime_plugin.WindowCommand):
	def run(self):
		favorites = Schemr.get_favorites()
		favorites.append(Schemr.get_scheme())
		Schemr.set_favorites(favorites)

	def is_enabled(self):
		return Schemr.get_scheme() not in Schemr.get_favorites()

class SchemrUnfavoriteCurrentSchemeCommand(sublime_plugin.WindowCommand):
	def run(self):
		favorites = Schemr.get_favorites()
		favorites.remove(Schemr.get_scheme())
		Schemr.set_favorites(favorites)

	def is_enabled(self):
		return Schemr.get_scheme() in Schemr.get_favorites()

	# Cycles the full list of schemes that are available
	# regardless of whether or not they are favorited.
class SchemrCycleSchemesCommand(sublime_plugin.WindowCommand):
	def run(self, direction):
		Schemr.cycle_schemes(Schemr.load_schemes(), direction)

	# Cycles the list of schemes that have been favorited. This command is
	# only available if the number of favorites is enough to cycle through.
class SchemrCycleFavoriteSchemesCommand(sublime_plugin.WindowCommand):
	def run(self, direction):
		Schemr.cycle_schemes([scheme for scheme in Schemr.load_schemes() if scheme[2]], direction)

	def is_enabled(self):
		return len(Schemr.get_favorites()) > 1

	# These commands are provided for backwards-compatibility.
	# SchemrCycleSchemeCommand should be used instead.
class SchemrNextSchemeCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.window.run_command('schemr_cycle_schemes', {'direction': 'next'})
class SchemrPreviousSchemeCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.window.run_command('schemr_cycle_schemes', {'direction': 'prev'})
class SchemrRandomSchemeCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.window.run_command('schemr_cycle_schemes', {'direction': 'rand'})
