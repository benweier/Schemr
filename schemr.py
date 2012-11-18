import sublime, sublime_plugin
import os
import json
import threading

settings = sublime.load_settings('Preferences.sublime-settings')

class ScanFiles(threading.Thread):
	def run(self):
		packages_path = sublime.packages_path()
		for root, dirs, files in os.walk(packages_path):
			for filename in files:
				if filename.endswith('.tmTheme'):
					path = os.path.split(root)[1] + '/' + filename
					if root != packages_path:
						path = 'Packages' + '/' + path
					Schemr.commands.append({'caption': 'Schemr: ' + os.path.splitext(filename)[0], 'command': 'switch_scheme', 'args': { 's': path }})

		Schemr.commands.append({'caption': 'Schemr: Reload schemes', 'command': 'reload_schemes'})

		c = open(os.path.join(packages_path, 'Schemr', 'Default.sublime-commands'), 'w')
		c.write(json.dumps(Schemr.commands, indent = 4) + '\n')
		c.close

class Schemr:
	def load(self):
		Schemr.scheme = settings.get('color_scheme')
		Schemr.commands = []
		thread = ScanFiles()
		thread.start()

Schemr = Schemr()
sublime.set_timeout(Schemr.load, 3000)

class SwitchSchemeCommand(sublime_plugin.ApplicationCommand):
	def run(self, s):
		if self.get_scheme() != s:
			self.set_scheme(s)

	def get_scheme(self):
		return settings.get('color_scheme', 'Packages/Color Scheme - Default/Monokai.tmTheme')

	def set_scheme(self, s):
		settings.set('color_scheme', s)
		sublime.save_settings('Preferences.sublime-settings')

class ReloadSchemesCommand(sublime_plugin.ApplicationCommand):
	def run(self):
		Schemr.load()
