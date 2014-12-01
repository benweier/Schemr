# About
[![Gitter](https://badges.gitter.im/Join Chat.svg)](https://gitter.im/benweier/Schemr?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
Schemr allows you to quickly change your color scheme using the command palette and keyboard shortcuts. With Schemr, you get commands to easily cycle forward, backward and randomly through your available color schemes.

# Features
* Full compatibility with Sublime Text 2 and 3.
* Previews the selected color scheme as you navigate up/down through the quick panel. [ST3 ONLY]
* Allows color schemes to be favorited for even faster access.
* Displays `[Dark]` or `[Light]` in the scheme list to easily filter by type.
* Automatically loads all available `.tmTheme` files, including those found inside `.sublime-package` files.

# Installation
Install Schemr through [Package Control](https://sublime.wbond.net/), or download and extract it into your Sublime Text `Packages` folder.

# Contributors
* [Max](https://github.com/SyntaxColoring) - Favorites support and code refactoring

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

# User Settings
These settings are available to control some of Schemr's behaviour. Add them to `Preferences.sublime-settings` if you wish to override the default value.

`schemr_brightness_threshold`: Integer 0-255. Defaults to 100.

The brightness theshold setting allows you to define where the cutoff occurs between Dark and Light themes. Higher values indicate increasing brightess approaching white rgb(255, 255, 255), while lower values indicate decreasing brightess approaching black rgb(0, 0, 0).

`schemr_brightness_flags`: Boolean true|false. Defaults to true.

The brightness flags setting allows you to disable the "[Dark]" or "[Light]" text that appears after the scheme name in the quick panel. Disabling this will turn off colour scheme parsing entirely and may increase performance if you have a large number of schemes.

`schemr_preview_selection`: Boolean true|false. Defaults to true.

If you are using Sublime Text 3, you can enable/disable previewing the highlighted colour scheme as you move up/down through the list if you don't like the preview functionality or experience performance issues.

# Note about [SublimeLinter](https://sublime.wbond.net/packages/SublimeLinter)

To improve the user experience, Schemr filters schemes that contain `(SL)` from being listed or activated with Schemr commands. These schemes can still be enabled manually through the application menu or user settings file.

If a colour scheme does not define colours for the [SublimeLinter](https://sublime.wbond.net/packages/SublimeLinter) plugin, it will be extended and the updated scheme written to a file with `(SL)` appended to the name. If you have a lot of schemes and switch between them frequently this can quickly pollute the scheme list with many duplicates. You only need to activate the base colour scheme and SublimeLinter will switch to the `(SL)` version automatically.
