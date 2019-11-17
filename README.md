# cdm-pylint-plugin
The project is a [Codimension Python IDE](http://codimension.org) pylint plugin.

With this plugin the functionality of running pylint for a saved file is
available in the IDE.

# Installation
The plugin is pip installable:

```bash
pip install cdmpylintplugin
```

There is a little value (if any) to install it without the
[Codimension IDE](http://codimension.org).

When installed with Codimension python IDE the following ways are available
to invoke the pylint analysis:

- Ctrl+C when the current buffer is a python file
- The current buffer context menu
- The main menu `Tools->Pylint`
- The buffer toolbar button

Also, a pylintrc configuration file can be generated of edited. The options
are available via a buffer context menu.
