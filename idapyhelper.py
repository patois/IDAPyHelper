import idaapi
import ida_kernwin

__author__ = "Dennis Elser"

class PyHelperChooser(ida_kernwin.Choose2):
    def __init__(self, title, nb=5):
        ida_kernwin.Choose2.__init__(self,
                        title,
                        [ ["Module", 10], ["Symbol", 20], ["Docstring", 30] ],
                        width=30, height=6)
        self.items = []
        for symbol in dir(idaapi):
            try:
                attr = getattr(idaapi, symbol)
                docstr = attr.__doc__
                module = attr.__module__
            except AttributeError as ae:
                docstr = ""
                module = ""

            self.items.append([module,
                symbol,
                docstr.lstrip() if docstr else ""])
        self.icon = 0

    def OnGetLine(self, n):
        return self.items[n]

    def OnGetSize(self):
        return len(self.items)

    def OnSelectLine(self, n):
        module = self.items[n][0]
        symbol = self.items[n][1]
        docstring = self.items[n][2]
        postfix = " (%s)" % module if len(module) else ""
        if not len(docstring):
            ida_kernwin.msg("No docstring available for \"%s\"\n" % symbol)
        else:
            f = DocstringViewer("%s%s" % (symbol, postfix), docstring)
            f.modal = False
            f.openform_flags = ida_kernwin.PluginForm.FORM_TAB
            f, args = f.Compile()
            f.Open()

        return (ida_kernwin.Choose.NOTHING_CHANGED, )

class DocstringViewer(ida_kernwin.Form):
    def __init__(self, title, docstr):
        ida_kernwin.Form.__init__(self,
("BUTTON YES NONE\n"
"BUTTON NO NONE\n"
"BUTTON CANCEL NONE\n"
"Docstring for: %s\n\n"
"<##Enter text##:{cbEditable}>"
) % title,
{'cbEditable': ida_kernwin.Form.MultiLineTextControl(text=docstr,
    flags=ida_kernwin.textctrl_info_t.TXTF_READONLY |
    ida_kernwin.textctrl_info_t.TXTF_FIXEDFONT)})


try:
    pyhelper
except:
    pyhelper=PyHelperChooser("IDAPyHelper")

pyhelper.Show()