import sublime, sublime_plugin
import os, zipfile
from random import random

	# Contains various common, internal functions for Schemr.
class Schemr():
		# Returns a list of all managed schemes.  Each scheme is itself represented by a list
		# that contains, in order, (1) its pretty-printed name, (2) its path and (3) whether
		# or not it is favorited (True or False).
	def load_schemes(self):
		all_scheme_paths = []
		
		# Load the paths for schemes contained in folders.
		for root, dirs, files in os.walk(sublime.packages_path()):
			for filename in (filename for filename in files if filename.endswith('.tmTheme')):
				filepath = os.path.join(root, filename).replace(sublime.packages_path(), 'Packages').replace('\\', '/')
				all_scheme_paths.append(filepath)
		
		# Load the paths for schemes contained in zipped .sublime-package files.
		for root, dirs, files in os.walk(sublime.installed_packages_path()):
			for package in (package for package in files if package.endswith('.sublime-package')):
				zf = zipfile.ZipFile(os.path.join(sublime.installed_packages_path(), package))
				for filename in (filename for filename in zf.namelist() if filename.endswith('.tmTheme')):
					filepath = os.path.join(root, package, filename).replace(sublime.installed_packages_path(), 'Packages').replace('.sublime-package', '').replace('\\', '/')
					all_scheme_paths.append(filepath)
		
		# Load the paths for color schemes that ship with Sublime Text.
		default_schemes = os.path.join(os.getcwd(), 'Packages', 'Color Scheme - Default.sublime-package')
		if os.path.exists(default_schemes):
			zf = zipfile.ZipFile(default_schemes)
			for filename in (filename for filename in zf.namelist() if filename.endswith('.tmTheme')):
				filepath = os.path.join('Packages', 'Color Scheme - Default', filename).replace('\\', '/')
				all_scheme_paths.append(filepath)
		
		# The list of favorite schemes is stored in its own settings file.
		favorite_scheme_paths = self.get_favorite_schemes()
		
		# Given the paths of all the color schemes, add in the information for
		# the pretty-printed name and whether or not it's been favorited.
		all_schemes = []
		for scheme_path in all_scheme_paths:
			favorited = scheme_path in favorite_scheme_paths
			pretty_name = 'Scheme: ' + scheme_path.split('/').pop().replace('.tmTheme', '')
			if favorited: pretty_name += u' \N{BLACK STAR}' # Put a pretty star icon next to favorited schemes.  :)
			all_schemes.append([pretty_name, scheme_path, favorited])
			
		all_schemes.sort()
		return all_schemes
	
		# Returns a list of the paths of all the schemes the user has favorited.
	def get_favorite_schemes(self):
		# The favorites list is stored in its own settings file to avoid cluttering the global Sublime Text preferences.
		return sublime.load_settings('SchemrFavorites.sublime-settings').get('schemr_favorites', [])
	
		# Sets and saves the user's favorites list.
	def set_favorite_schemes(self, favorite_schemes):
		settings = sublime.load_settings('SchemrFavorites.sublime-settings')
		settings.set('schemr_favorites', favorite_schemes)
		sublime.save_settings('SchemrFavorites.sublime-settings')
	
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
		color_schemes = [[scheme[0], scheme[1]] for scheme in schemes]
		
		the_scheme = self.get_scheme()
		
		# If the active scheme isn't part of the supplied pool (the schemes variable),
		# then we can't skip the selection to that point and the best we can do is
		# start from the top of the list.
		the_index = None
		try: the_index = [scheme[1] for scheme in color_schemes].index(the_scheme)
		except (ValueError): the_index = 0
	
		def on_done(index):
			if index != -1:
				self.set_scheme(color_schemes[index][1])
				sublime.status_message(color_schemes[index][0])
			
			if index == -1:
				self.set_scheme(the_scheme)
	
		def on_select(index):
			self.set_scheme(color_schemes[index][1])
		
		try: # Attempt to enable preview-on-selection (only supported by Sublime Text 3).
			window.show_quick_panel(color_schemes, on_done, 0, the_index, on_select)
		except:
			window.show_quick_panel(color_schemes, on_done)
	
		# Sets the active scheme.
	def set_scheme(self, s):
		self.settings().set('color_scheme', s)
		sublime.save_settings('Preferences.sublime-settings')
	
		# Gets the active scheme.
	def get_scheme(self):
		return self.settings().get('color_scheme')
	
		# Returns the Sublime Text application settings object.
	def settings(self):
		return sublime.load_settings('Preferences.sublime-settings')

Schemr = Schemr()

class SchemrListSchemesCommand(sublime_plugin.WindowCommand):
	def run(self):
		Schemr.list_schemes(self.window, Schemr.load_schemes())

class SchemrListFavoriteSchemesCommand(sublime_plugin.WindowCommand):
	def run(self):
		Schemr.list_schemes(self.window, [scheme for scheme in Schemr.load_schemes() if scheme[2]])
	def is_enabled(self):
		return len(Schemr.get_favorite_schemes()) >= 1

	# SchemrFavoriteCurrentSchemeComand and SchemrUnfavoriteCurrentSchemeCommand
	# work in conjunction.  Only one is ever available to the user at a time,
	# depending on whether or not his active scheme is already favorited.
class SchemrFavoriteCurrentSchemeCommand(sublime_plugin.WindowCommand):
	def run(self):
		favorites = Schemr.get_favorite_schemes()
		favorites.append(Schemr.get_scheme())
		Schemr.set_favorite_schemes(favorites)
	def is_enabled(self):
		return Schemr.get_scheme() not in Schemr.get_favorite_schemes()
class SchemrUnfavoriteCurrentSchemeCommand(sublime_plugin.WindowCommand):
	def run(self):
		favorites = Schemr.get_favorite_schemes()
		favorites.remove(Schemr.get_scheme())
		Schemr.set_favorite_schemes(favorites)
	def is_enabled(self):
		return Schemr.get_scheme() in Schemr.get_favorite_schemes()
	
	# Cycles the scheme in the given direction ("next", "prev" or "rand").
class SchemrCycleSchemesCommand(sublime_plugin.WindowCommand):
	def run(self, direction):
		color_schemes = Schemr.load_schemes()
		the_scheme = Schemr.get_scheme()
		num_of_schemes = len(color_schemes)
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
		
	# Same as SchemrCycleSchemesCommand, but skips schemes that aren't favorited.
class SchemrCycleFavoriteSchemesCommand(sublime_plugin.WindowCommand):
	def run(self, direction):
		color_schemes = Schemr.load_schemes()
		the_scheme = Schemr.get_scheme()
		num_of_schemes = len(color_schemes)
		
		try:
			the_index = [scheme[1] for scheme in color_schemes].index(the_scheme)
		except (ValueError):
			the_index = 0

		if direction == 'rand':
			# Filter out non-favorites to select a random favorite.
			favorite_color_schemes = [scheme for scheme in color_schemes if scheme[2]]
			index = int(random() * len(favorite_color_schemes))
			Schemr.set_scheme(favorite_color_schemes[index][1])
			sublime.status_message(favorite_color_schemes[index][0])
		else:
			index = the_index
			if direction == 'next':
				for iteration in range(0, num_of_schemes):
					index = index + 1
					if index >= num_of_schemes: index = 0
					if color_schemes[index][2]: break # Stop on the first favorite found.
			elif direction == 'prev':
				for iteration in range(0, num_of_schemes):
					index = index - 1
					if index < 0: index = num_of_schemes - 1
					if color_schemes[index][2]: break # Stop on the first favorite found.
			Schemr.set_scheme(color_schemes[index][1])
			sublime.status_message(color_schemes[index][0])
		
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
