import idaapi

__author__ = "Dennis Elser"

class PyHelperChooser(idaapi.Choose2):
    def __init__(self, title, nb=5):
        idaapi.Choose2.__init__(self,
                        title,
                        [ ["Module", 10], ["Symbol", 20], ["Documentation", 30] ],
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
            idaapi.msg("No documentation available for \"%s\"\n" % symbol)
        else:
            f = DocstringViewer("%s%s" % (symbol, postfix), docstring)
            f.modal = False
            f.openform_flags = idaapi.PluginForm.FORM_TAB
            f, args = f.Compile()
            f.Open()
        return (idaapi.Choose.NOTHING_CHANGED, )

class DocstringViewer(idaapi.Form):
    def __init__(self, title, docstr):
        idaapi.Form.__init__(self,
("BUTTON YES NONE\n"
"BUTTON NO NONE\n"
"BUTTON CANCEL NONE\n"
"%s\n\n"
"<##Docstring##:{cbEditable}>"
) % title,
{'cbEditable': idaapi.Form.MultiLineTextControl(text=docstr,
    flags=idaapi.textctrl_info_t.TXTF_READONLY |
    idaapi.textctrl_info_t.TXTF_FIXEDFONT)})

try:
    pyhelper
except:
    pyhelper=PyHelperChooser("IDAPyHelper")

pyhelper.Show()