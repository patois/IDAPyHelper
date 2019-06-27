import ida_kernwin, ida_diskio
import os

__author__ = "Dennis Elser"

# --------------------------------------------------------------------------
class DocstringViewer(ida_kernwin.Form):
    """A form that displays a docstring."""
    def __init__(self, title, docstr):
        idaapi.Form.__init__(self,
("BUTTON YES NONE\n"
"BUTTON NO NONE\n"
"BUTTON CANCEL NONE\n"
"%s\n\n"
"<##Docstring##:{cbEditable}>"
) % title,
{'cbEditable': ida_kernwin.Form.MultiLineTextControl(text=docstr,
    flags=ida_kernwin.textctrl_info_t.TXTF_READONLY |
    ida_kernwin.textctrl_info_t.TXTF_FIXEDFONT)})

# --------------------------------------------------------------------------
class PyHelperChooser(ida_kernwin.Choose2):
    """A chooser filled with information about IDAPython bindings.
    Output is supposed to be filtered with Ctrl-F."""
    def __init__(self, title, nb=5):
        ida_kernwin.Choose2.__init__(self,
                        title,
                        [ ["Module", 10 | ida_kernwin.Choose.CHCOL_PLAIN],
                        ["Symbol", 20 | ida_kernwin.Choose.CHCOL_PLAIN],
                        ["Documentation", 30 | ida_kernwin.Choose.CHCOL_PLAIN] ],
                        width=30, height=6)
        self.items = []
        self.icon = 0
        self.build_items()

    def build_items(self):
        pydir = ida_diskio.idadir("python")
        for name in os.listdir(pydir):
            if name.endswith(".py"):
                name, _ = os.path.splitext(name)
                if name not in ["init", "idaapi"]:
                    mod = __import__(name)
                    for symbol in dir(mod):
                        try:
                            attr = getattr(mod, symbol)
                            docstr = attr.__doc__
                            module = attr.__module__
                        except AttributeError:
                            docstr = ""
                            module = ""
                        except NameError:
                            docstr = ""
                            module = ""

                        if not module.startswith("_"):
                            self.items.append((module,
                                symbol,
                                docstr.strip() if docstr else ""))

    def OnGetLine(self, n):
        module, symbol, docstring = self.items[n]
        return [module,
            symbol,
            docstring.replace("\n", " ")]

    def OnGetSize(self):
        return len(self.items)

    def OnSelectLine(self, n):
        module, symbol, docstring = self.items[n]
        postfix = " (%s)" % module if len(module) else ""
        if not len(docstring):
            ida_kernwin.msg("No documentation available for \"%s\"\n" % symbol)
        else:
            f = DocstringViewer("%s%s" % (symbol, postfix), docstring)
            f.modal = False
            f.openform_flags = ida_kernwin.PluginForm.FORM_TAB
            f, args = f.Compile()
            f.Open()
        return (ida_kernwin.Choose.NOTHING_CHANGED, )

try:
    pyhelper
except:
    pyhelper=PyHelperChooser("IDAPyHelper")

pyhelper.Show()