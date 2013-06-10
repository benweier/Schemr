import sublime, sublime_plugin
import os, zipfile
from random import random
from time import sleep

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
		favorite_scheme_paths = sublime.load_settings('SchemrFavorites.sublime-settings').get('schemr_favorites')
		
		# Given the paths of all the color schemes, add in the information for
		# the pretty-printed name and whether or not it's been favorited.
		all_schemes = []
		for scheme_path in all_scheme_paths:
			favorited = scheme_path in favorite_scheme_paths
			pretty_name = "Scheme: " + scheme_path.split("/").pop().replace('.tmTheme', '')
			if favorited: pretty_name += " ★"
			all_schemes.append([pretty_name, scheme_path, favorited])
			
		all_schemes.sort()
		return all_schemes

	def set_scheme(self, s):
		self.settings().set('color_scheme', s)
		sublime.save_settings('Preferences.sublime-settings')

	def get_scheme(self):
		return self.settings().get('color_scheme')

	def settings(self):
		return sublime.load_settings('Preferences.sublime-settings')

Schemr = Schemr()

class SchemrListSchemesCommand(sublime_plugin.WindowCommand):
	def run(self):
		# Discard favorites information for listing schemes.
		color_schemes = [[scheme[0], scheme[1]] for scheme in Schemr.load_schemes()]
		
		the_scheme = Schemr.get_scheme()
		the_index = [scheme[1] for scheme in color_schemes].index(the_scheme)

		def on_done(index):
			if index != -1:
				Schemr.set_scheme(color_schemes[index][1])
				sublime.status_message(color_schemes[index][0])

			if index == -1:
				Schemr.set_scheme(color_schemes[the_index][1])

		def on_select(index):
			Schemr.set_scheme(color_schemes[index][1])

		try:
			self.window.show_quick_panel(color_schemes, on_done, 0, the_index, on_select)
		except:
			self.window.show_quick_panel(color_schemes, on_done)

	# Cycles the scheme in the given direction ("next", "prev" or "rand").
class SchemrCycleSchemeCommand(sublime_plugin.WindowCommand):
	def run(self, direction):
		color_schemes = Schemr.load_schemes()
		the_scheme = Schemr.get_scheme()
		num_of_schemes = len(color_schemes)
		try:
			the_index = [scheme[1] for scheme in color_schemes].index(the_scheme)
		except (ValueError):
			the_index = 0

		if direction == "next":
			index = the_index + 1 if the_index < num_of_schemes - 1 else 0

		if direction == "prev":
			index = the_index - 1 if the_index > 0 else num_of_schemes - 1

		if direction == "rand":
			index = int(random() * len(color_schemes))

		Schemr.set_scheme(color_schemes[index][1])
		sublime.status_message(color_schemes[index][0])
		
# These commands are provided for backwards-compatibility.
# SchemrCycleSchemeCommand should be used instead.
class SchemrNextSchemeCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.window.run_command("schemr_cycle_scheme", {"direction": "next"})
class SchemrPreviousSchemeCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.window.run_command("schemr_cycle_scheme", {"direction": "prev"})
class SchemrRandomSchemeCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.window.run_command("schemr_cycle_scheme", {"direction": "rand"})
