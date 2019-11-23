# IDAPyHelper

IDAPyHelper is a script for the Interactive Disassembler that helps writing IDAPython scripts and plugins.

It does so by acquiring all names accessible via IDAPython and makes them available in a browsable list that can be sorted, scanned (Alt-T) and filtered (Ctrl-F) arbitrarily. Double clicking a list entry opens a separate view that displays the entry's docstring, if available. Pressing Alt-E opens the entire module for viewing.

This IDAPython project is compatible with Python3. For compatibility with older versions of IDA, you may want to check out the Python2 branch of this project.

![IDAPyHelper animated gif](/rsrc/pyhelper.gif?raw=true)