import sublime, sublime_plugin
import os, zipfile

class Schemr():
	def load_schemes(self):
		color_schemes = []

		for root, dirs, files in os.walk(sublime.packages_path()):
			for filename in (filename for filename in files if filename.endswith('.tmTheme')):
				name = filename.replace('.tmTheme', '')
				filepath = os.path.join(root, filename).replace(sublime.packages_path(), 'Packages').replace('\\', '/')
				color_schemes.append(['Scheme: ' + name, filepath])

		for root, dirs, files in os.walk(sublime.installed_packages_path()):
			for package in (package for package in files if package.endswith('.sublime-package')):
				zf = zipfile.ZipFile(os.path.join(sublime.installed_packages_path(), package))
				for filename in (filename for filename in zf.namelist() if filename.endswith('.tmTheme')):
					name = os.path.basename(filename).replace('.tmTheme', '')
					filepath = os.path.join(root, package, filename).replace(sublime.installed_packages_path(), 'Packages').replace('.sublime-package', '').replace('\\', '/')
					color_schemes.append(['Scheme: ' + name, filepath])

		return color_schemes

	def set_scheme(self, s):
		self.settings().set('color_scheme', s)
		sublime.save_settings('Preferences.sublime-settings')

	def get_scheme(self):
		return self.settings().get('color_scheme')

	def cycle_scheme(self, d):
		color_schemes = self.load_schemes()
		the_scheme = self.get_scheme()
		the_index = [scheme[1] for scheme in color_schemes].index(the_scheme)
		num_of_schemes = len(color_schemes)

		if d == 1:
			index = the_index + 1 if the_index < num_of_schemes - 1 else 0

		if d == -1:
			index = the_index - 1 if the_index > 0 else num_of_schemes - 1

		self.set_scheme(color_schemes[index][1])
		sublime.status_message(color_schemes[index][0])

	def settings(self):
		return sublime.load_settings('Preferences.sublime-settings')

Schemr = Schemr()

class SchemrListSchemesCommand(sublime_plugin.WindowCommand):
	def run(self):
		color_schemes = Schemr.load_schemes()

		def on_done(index):
			if index != -1:
				Schemr.set_scheme(color_schemes[index][1])
				sublime.status_message(color_schemes[index][0])

		self.window.show_quick_panel(color_schemes, on_done)

class SchemrNextSchemeCommand(sublime_plugin.WindowCommand):
	def run(self):
		Schemr.cycle_scheme(1)

class SchemrPrevSchemeCommand(sublime_plugin.WindowCommand):
	def run(self):
		Schemr.cycle_scheme(-1)
