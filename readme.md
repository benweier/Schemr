# About
[![Gitter](https://badges.gitter.im/Join Chat.svg)](https://gitter.im/benweier/Schemr?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Schemr allows you to quickly change your color scheme using the command palette and keyboard shortcuts. With Schemr, you get commands to easily cycle forward, backward and randomly through your available color schemes.

# Features
* Full compatibility with Sublime Text 2 and 3.
* Preview the selected color scheme as you navigate through the quick panel. [ST3 ONLY]
* Color schemes can be favorited for even faster access.
* Set syntax-specific color schemes for your favorite languages. Use your favorite schemes for your favorite languages!
* Displays `[Dark]` or `[Light]` in the scheme list to easily filter by type.
* Automatically loads all available `.tmTheme` files, including those found inside `.sublime-package` files.

# Installation
Install Schemr through [Package Control](https://packagecontrol.io/), or download and extract it into your Sublime Text `Packages` folder.

# Contributors
* [Max](https://github.com/SyntaxColoring) - Favorites support and code refactoring
* [River](https://github.com/RheingoldRiver) - Cycle themes for current syntax via keymap

# Usage

**Schemr: List schemes** displays all the available schemes in alphabetical order.

* Default binding: <kbd>Alt+F5</kbd> (Windows/Linux) <kbd>Option+F5</kbd> (OSX)

**Schemr: Next scheme** switches immediately to the alphabetically next color scheme.

* Default binding: <kbd>Alt+F7</kbd> (Windows/Linux) <kbd>Option+F7</kbd> (OSX)

**Schemr: Previous scheme** switches immediately to the alphabetically previous color scheme.

* Default binding: <kbd>Alt+F8</kbd> (Windows/Linux) <kbd>Option+F8</kbd> (OSX)

**Schemr: Random scheme** switches immediately to a random color scheme that you have installed.

* Default binding: <kbd>Alt+F10</kbd> (Windows/Linux) <kbd>Option+F10</kbd> (OSX)

## Favorites

**Schemr: Add current scheme to favorites** and **Schemr: Remove current scheme from favorites** add and remove the currently selected color scheme to your favorites list.

* You can also edit your favorites list manually through **Preferences > Package Settings > Schemr**.

**Schemr: List favorite schemes** displays your favorite schemes in alphabetical order.

* Default binding: <kbd>Alt+Shift+F5</kbd> (Windows/Linux) <kbd>Option+Shift+F5</kbd> (OSX)

**Schemr: Next favorite scheme** switches immediately to the alphabetically next color scheme in your favorites.

* Default binding: <kbd>Alt+Shift+F7</kbd> (Windows/Linux) <kbd>Option+Shift+F7</kbd> (OSX)

**Schemr: Previous favorite scheme** switches immediately to the alphabetically previous color scheme in your favorites.

* Default binding: <kbd>Alt+Shift+F8</kbd> (Windows/Linux) <kbd>Option+Shift+F8</kbd> (OSX)

**Schemr: Random favorite scheme** switches immediately to a random color scheme in your favorites.

* Default binding: <kbd>Alt+Shift+F10</kbd> (Windows/Linux) <kbd>Option+Shift+F10</kbd> (OSX)

## Syntax Specific Settings

Syntax specific color schemes will override the behavior of all other commands for listing and switching schemes! Reset the syntax specific scheme setting to return to the normal behavior.

**Schemr: Set scheme for current syntax** displays the scheme selection list to choose a color scheme for the syntax mode of the current file.

**Schemr: Reset scheme for current syntax** removes the color scheme setting for the syntax mode of the current file. Only available if a syntax specific color scheme has been set.

**schemer\_cycle\_syntax\_schemes** is available for use as a keyboard shortcut. You can specify a direction and a filter (suggested filters are `Light` or `Dark`, but any string from theme names is allowed).

Example keymap that you could copy to your `sublime-keymap` file (however no defaults are provided):

```json
	{
		"keys": ["ctrl+k", "ctrl+o"], "command": "schemr_cycle_syntax_schemes",
		"args": { "direction": "next", "filter": "Dark" }
	},
	{
		"keys": ["ctrl+k", "ctrl+p"], "command": "schemr_cycle_syntax_schemes",
		"args": { "direction": "prev", "filter": "Dark" }
	},
```

# User Settings
These settings are available to control some of Schemr's behavior. Add them to `Preferences.sublime-settings` if you wish to override the default value.

`schemr_brightness_threshold`: Integer 0-255. Defaults to 100.

The brightness theshold setting allows you to define where the cutoff occurs between Dark and Light themes. Higher values indicate increasing brightess approaching white, while lower values indicate decreasing brightess approaching black.

`schemr_brightness_flags`: Boolean true|false. Defaults to true.

The brightness flags setting allows you to disable the "[Dark]" or "[Light]" text that appears after the scheme name in the quick panel. Disabling this will turn off color scheme parsing entirely and may increase performance if you have a large number of schemes.

`schemr_preview_selection`: Boolean true|false. Defaults to true.

If you are using Sublime Text 3, you can enable/disable previewing the highlighted color scheme as you move through the scheme list. Some performance issues related to the SublimeLinter and Color Highlighter plugins may be resolved by disabling this setting.

# Note about [SublimeLinter](https://packagecontrol.io/packages/SublimeLinter) and [Color Highlighter](https://packagecontrol.io/packages/Color%20Highlighter)

To improve the user experience, Schemr filters schemes that contain `(SL)` or `(Color Highlighter)` from being listed or activated with Schemr commands. These schemes can still be enabled manually through the application menu or user settings file.

If a color scheme does not define colors for the [SublimeLinter](https://packagecontrol.io/packages/SublimeLinter) or [Color Highlighter](https://packagecontrol.io/packages/Color%20Highlighter), the scheme file is extended and the written to a file in the `Packages/User` directory. If you switch between a lot of schemes this can quickly pollute the scheme list with many duplicates. Activate the base color scheme through Schemr and SublimeLinter/Color Highlighter will switch to their version automatically.
