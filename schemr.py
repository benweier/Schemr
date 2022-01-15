import os
import re
import sys
import zipfile
from random import random

import sublime
import sublime_plugin

is_ST2 = int(sublime.version()) < 3000

if not is_ST2:
    import Schemr.lib.plist_parser as parser
else:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
    import plist_parser as parser


class Schemr(object):
    """
    Contains various common, internal functions for Schemr.
    """
    _instance = None

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.preferences = dict(filename='Preferences.sublime-settings',
                                data=sublime.load_settings('Preferences.sublime-settings'))
        self.favorites = dict(filename='SchemrFavorites.sublime-settings',
                              data=sublime.load_settings('SchemrFavorites.sublime-settings'))

    def load_schemes(self):
        """
        Returns a list of all managed schemes.  Each scheme is itself represented by a list
        that contains, in order, (1) its pretty-printed name, (2) its path and (3) whether
        or not it is favorited (True or False).
        """
        scheme_paths = []
        favorites = self.get_favorites()

        try:  # use find_resources() first for ST3.
            scheme_paths = sublime.find_resources('*.tmTheme')

        except:  # fallback to walk() for ST2
            # Load the paths for schemes contained in zipped .sublime-package files.
            for root, dirs, files in os.walk(sublime.installed_packages_path()):
                for package in (package for package in files if package.endswith('.sublime-package')):
                    zf = zipfile.ZipFile(os.path.join(sublime.installed_packages_path(), package))
                    for filename in (filename for filename in zf.namelist() if filename.endswith('.tmTheme')):
                        filepath = os.path.join(root, package, filename).replace(
                            sublime.installed_packages_path(),
                            'Packages').replace('.sublime-package', '').replace('\\', '/')
                        scheme_paths.append(filepath)

            # Load the paths for schemes contained in folders.
            for root, dirs, files in os.walk(sublime.packages_path()):
                for filename in (filename for filename in files if filename.endswith('.tmTheme')):
                    filepath = os.path.join(root, filename).replace(
                        sublime.packages_path(), 'Packages').replace('\\', '/')
                    scheme_paths.append(filepath)

        scheme_paths = self.filter_scheme_list(scheme_paths)

        # Given the paths of all the color schemes, add in the information for
        # the pretty-printed name and whether or not it's been favorited.
        schemes = []
        for scheme_path in scheme_paths:
            scheme_name = self.filter_scheme_name(scheme_path)
            is_favorite = ''
            if scheme_path in favorites: is_favorite = u'   \u2605'  # Put a pretty star icon next to favorited schemes. :)
            schemes.append([scheme_name, scheme_path, is_favorite])

        schemes.sort(key=lambda s: s[0].lower())
        return schemes

    def list_schemes(self, window: sublime.Window, schemes, preferences):
        """
        Displays the given schemes in a quick-panel, letting the user cycle through
        them to preview them and possibly select one.  The reason that this is a method
        here instead of a free-standing command is that the "List all schemes" and
        "List favorite schemes" commands function exactly the same except for the
        underlying schemes that they operate on.  This method exists to provide that
        common listing functionality.
        """

        # Get the user-defined settings or return default values.
        schemr_brightness_theshold = self.preferences.get('data').get('schemr_brightness_theshold', 100)
        schemr_brightness_flags = self.preferences.get('data').get('schemr_brightness_flags', True)
        schemr_preview_selection = self.preferences.get('data').get('schemr_preview_selection', True)

        the_scheme_path = self.get_scheme(preferences)
        the_scheme_name = self.filter_scheme_name(the_scheme_path)

        # If the active scheme isn't part of the scheme list, then we can't skip the
        # selection to that point and the best we can do is start from the top of the list.
        try:
            the_index = [scheme[0] for scheme in schemes].index(the_scheme_name)
        except ValueError:
            the_index = 0

        # Build the display list of color schemes.
        if schemr_brightness_flags:
            color_schemes = list()

            # Add a brightness flag to each scheme name if the luminance
            # is above or below the schemr_brightness_threshold value.
            for scheme in schemes:
                # Get the RGB value of the scheme background and convert to luminance value.
                rgb = self.parse_scheme(scheme[1])
                flag = ''

                if rgb is not False:
                    luminance = (0.2126 * rgb[0]) + (0.7152 * rgb[1]) + (0.0722 * rgb[2])
                    if luminance < schemr_brightness_theshold:
                        flag = '   [Dark]'
                    else:
                        flag = '   [Light]'

                color_schemes.append([scheme[0] + flag + scheme[2], scheme[1]])

        else:
            color_schemes = [[scheme[0] + scheme[2], scheme[1]] for scheme in schemes]

        # Set a selection flag to detect when the panel is first opened in some
        # versions of Sublime Text. This prevents the color scheme from 'flickering'
        # from one scheme to another as the panel jumps to the active selection.
        self.user_selected = False

        def on_highlight(index):
            if self.user_selected is True:
                self.set_scheme(color_schemes[index][1], preferences)
            else:
                self.user_selected = True

        try:  # Attempt to enable preview-on-selection (only supported by Sublime Text 3).
            if schemr_preview_selection is True:
                window.show_quick_panel(color_schemes,
                                        lambda index: self.select_scheme(index, the_scheme_path, color_schemes,
                                                                         preferences), 0, the_index, on_highlight)
            else:
                window.show_quick_panel(color_schemes,
                                        lambda index: self.select_scheme(index, the_scheme_path, color_schemes,
                                                                         preferences), 0, the_index)
        except:
            window.show_quick_panel(color_schemes,
                                    lambda index: self.select_scheme(index, the_scheme_path, color_schemes,
                                                                     preferences))

    def select_scheme(self, index, the_scheme_path, color_schemes, preferences):
        if index is -1:
            # Restore or erase the original scheme setting.
            if the_scheme_path != '':
                self.set_scheme(the_scheme_path, preferences)
                sublime.save_settings(preferences.get('filename'))
            else:
                self.erase_scheme(preferences)
        else:
            # Persist the new scheme setting.
            self.set_scheme(color_schemes[index][1], preferences)
            sublime.save_settings(preferences.get('filename'))
            sublime.status_message('Scheme: ' + color_schemes[index][0])

    def cycle_schemes(self, schemes, direction, view: sublime.View = None, filter=None, preferences=None):
        """
        Cycles the scheme in the given direction ("next", "prev" or "rand").
        """
        if preferences is None:
            preferences = self.preferences
        the_scheme_name = self.filter_scheme_name(self.get_scheme(preferences))

        permissible_schemes = [scheme for scheme in schemes if
                               filter in scheme[0] or scheme[0] == the_scheme_name] if filter is not None else schemes

        num_of_schemes = len(permissible_schemes)

        # Try to find the current scheme path in the available schemes otherwise
        # start from the top of the list. Useful in case the user has manually
        # saved an invalid scheme path or the current scheme file is not available.
        try:
            the_index = [scheme[0] for scheme in permissible_schemes].index(the_scheme_name)
        except ValueError:
            the_index = 0

        if direction == 'next':
            index = the_index + 1 if the_index < num_of_schemes - 1 else 0

        if direction == 'prev':
            index = the_index - 1 if the_index > 0 else num_of_schemes - 1

        if direction == 'rand':
            index = int(random() * len(permissible_schemes))

        # set scheme for syntax
        self.set_scheme(permissible_schemes[index][1], preferences)

        # if a view is defined, reset the theme in the current view so we properly reset the preview.
        # this is optional in order to possibly preserve ST2 compatibility
        if view is not None:
            view.settings().erase("color_scheme")
        sublime.save_settings(preferences.get('filename'))
        sublime.status_message('Scheme: ' + permissible_schemes[index][0])

    @staticmethod
    def parse_scheme(scheme_path):
        """Parse the scheme file for the background color and return the RGB values
        in order to determine if the scheme is Dark or Light. Use load_resources()
        first for ST3 or fallback to the absolute path for ST2.
        """
        if not is_ST2:
            try:
                xml = sublime.load_resource(scheme_path)
            except:
                print('Error loading ' + scheme_path)
                return False
            try:
                plist = parser.parse_string(xml)
            except parser.PropertyListParseError:
                print('Error parsing ' + scheme_path)
                return False
        else:
            xml = os.path.join(sublime.packages_path(), scheme_path.replace('Packages/', ''))
            try:
                plist = parser.parse_file(xml)
            except parser.PropertyListParseError:
                print('Error parsing ' + scheme_path)
                return False

        try:
            background_color = plist['settings'][0]['settings']['background'].lstrip('#')
        except KeyError:  # tmTheme is missing a background color
            return False

        if len(background_color) == 3:
            # Shorthand value, e.g. #111
            # Repeat the values for correct base 16 conversion.
            r, g, b = [background_color[i:i + 1] * 2 for i in range(0, 3)]
        else:
            # Full-length color value, e.g. #111111 or #FFEEEEEE
            # Here we assume the order of hex values is #RRGGBB
            # or #RRGGBBAA and only use six characters.
            r, g, b = [background_color[i:i + 2] for i in range(0, 6, 2)]

        try:
            r, g, b = [int(n, 16) for n in (r, g, b)]
        except ValueError:  # Error converting the hex value
            return False

        return (r, g, b)

    @staticmethod
    def set_scheme(scheme, preferences):
        preferences.get('data').set('color_scheme', scheme)

    @staticmethod
    def get_scheme(preferences):
        return preferences.get('data').get('color_scheme', '')

    @staticmethod
    def erase_scheme(preferences):
        preferences.get('data').erase('color_scheme')

    def set_favorites(self, schemes):
        self.favorites.get('data').set('schemr_favorites', schemes)
        sublime.save_settings(self.favorites.get('filename'))

    def get_favorites(self):
        return self.favorites.get('data').get('schemr_favorites')

    @staticmethod
    def filter_scheme_name(scheme_path):
        regex = re.compile('(\ \(SL\))|(\ Color\ Highlighter)?.tmTheme', re.IGNORECASE)
        scheme_name = re.sub(regex, '', scheme_path).split('/').pop()
        return scheme_name

    @staticmethod
    def filter_scheme_list(scheme_list):
        # Filter schemes generated by known plugins.
        regex = re.compile('SublimeLinter|Color\ Highlighter|Colorsublime - Themes\/cache', re.IGNORECASE)
        return [scheme for scheme in scheme_list if not regex.search(scheme)]

    def find_scheme(self, scheme_path):
        scheme_name = self.filter_scheme_name(scheme_path)
        matching_paths = [path for name, path, favorited in self.load_schemes() if name == scheme_name]
        if len(matching_paths) is not 0:
            return matching_paths[0]
        else:
            return False


def plugin_loaded():
    """
    Called when Sublime API is ready [ST3].
    """
    Schemr.instance()


class SchemrListSchemesCommand(sublime_plugin.WindowCommand):
    """Display the full list of schemes available, regardless
    of whether or not they are favorited.
    """

    def run(self):
        Schemr.instance().list_schemes(self.window, Schemr.instance().load_schemes(), Schemr.instance().preferences)


class SchemrListFavoriteSchemesCommand(sublime_plugin.WindowCommand):
    """Display the list of schemes that have been favorited.
    Only available if there are favorites to display.
    """

    def run(self):
        Schemr.instance().list_schemes(self.window,
                                       [scheme for scheme in Schemr.instance().load_schemes() if scheme[2]],
                                       Schemr.instance().preferences)

    def is_enabled(self):
        return len(Schemr.instance().get_favorites()) > 0


class SchemrFavoriteCurrentSchemeCommand(sublime_plugin.WindowCommand):
    """
    Only available when SchemrUnfavoriteCurrentSchemeCommand isn't
    """

    def run(self):
        the_scheme = Schemr.instance().find_scheme(Schemr.instance().get_scheme(Schemr.instance().preferences))
        if the_scheme is not False:
            favorites = Schemr.instance().get_favorites()
            favorites.append(the_scheme)
            Schemr.instance().set_favorites(favorites)

    def is_enabled(self):
        return Schemr.instance().find_scheme(
            Schemr.instance().get_scheme(Schemr.instance().preferences)) not in Schemr.instance().get_favorites()


class SchemrUnfavoriteCurrentSchemeCommand(sublime_plugin.WindowCommand):
    """
    Only available when SchemrFavoriteCurrentSchemeCommand isn't
    """

    def run(self):
        the_scheme = Schemr.instance().find_scheme(Schemr.instance().get_scheme(Schemr.instance().preferences))
        if the_scheme is not False:
            favorites = Schemr.instance().get_favorites()
            favorites.remove(the_scheme)
            Schemr.instance().set_favorites(favorites)

    def is_enabled(self):
        return Schemr.instance().find_scheme(
            Schemr.instance().get_scheme(Schemr.instance().preferences)) in Schemr.instance().get_favorites()


class SchemrCycleSchemesCommand(sublime_plugin.WindowCommand):
    """Cycles the full list of schemes that are available
    regardless of whether or not they are favorited.
    """

    def run(self, direction, filter=None):
        Schemr.instance().cycle_schemes(Schemr.instance().load_schemes(), direction, self.view, filter=filter)


class SchemrCycleFavoriteSchemesCommand(sublime_plugin.WindowCommand):
    """Cycles the list of schemes that have been favorited. This command is
    only available if the number of favorites is enough to cycle through.
    """

    def run(self, direction, filter=None):
        Schemr.instance().cycle_schemes([scheme for scheme in Schemr.instance().load_schemes() if scheme[2]], direction,
                                        self.view,
                                        filter=filter)

    def is_enabled(self):
        return len(Schemr.instance().get_favorites()) > 1


class SchemrSetSyntaxSchemeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        syntax_path = self.view.settings().get('syntax')
        syntax_file = os.path.splitext(os.path.basename(syntax_path))[0] + '.sublime-settings'
        preferences = dict(filename=syntax_file, data=sublime.load_settings(syntax_file))

        Schemr.instance().list_schemes(self.view.window(), Schemr.instance().load_schemes(), preferences)


class SchemrCycleSyntaxSchemesCommand(sublime_plugin.TextCommand):
    def run(self, edit, direction, filter=None):
        syntax_path = self.view.settings().get('syntax')
        syntax_file = os.path.splitext(os.path.basename(syntax_path))[0] + '.sublime-settings'
        preferences = dict(filename=syntax_file, data=sublime.load_settings(syntax_file))

        Schemr.instance().cycle_schemes(Schemr.instance().load_schemes(), direction,
                                        self.view, filter=filter, preferences=preferences)


class SchemrResetSyntaxSchemeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        syntax_path = self.view.settings().get('syntax')
        syntax_file = os.path.splitext(os.path.basename(syntax_path))[0] + '.sublime-settings'

        sublime.load_settings(syntax_file).erase('color_scheme')
        sublime.save_settings(syntax_file)

    def is_enabled(self):
        syntax_path = self.view.settings().get('syntax')
        syntax_file = os.path.splitext(os.path.basename(syntax_path))[0] + '.sublime-settings'

        return sublime.load_settings(syntax_file).has('color_scheme')


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


if is_ST2:
    plugin_loaded()
