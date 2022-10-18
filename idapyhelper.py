import ida_kernwin, ida_diskio, ida_pro
import os, inspect, sys

__author__ = "Dennis Elser"

DBG = False

# -----------------------------------------------------------------------------
def is_ida_version(min_ver_required):
    return ida_pro.IDA_SDK_VERSION >= min_ver_required

# --------------------------------------------------------------------------
class FileViewer(ida_kernwin.Form):
    """A form that displays a text file's content."""
    def __init__(self, title, content):
        ida_kernwin.Form.__init__(self,
("BUTTON YES NONE\n"
"BUTTON NO NONE\n"
"BUTTON CANCEL NONE\n"
"%s\n\n"
"<##Docstring##:{cbEditable}>"
) % title,
{'cbEditable': ida_kernwin.Form.MultiLineTextControl(text=content,
    flags=ida_kernwin.textctrl_info_t.TXTF_READONLY |
    ida_kernwin.textctrl_info_t.TXTF_FIXEDFONT)})

# --------------------------------------------------------------------------
class DocstringViewer(ida_kernwin.Form):
    """A form that displays a docstring."""
    def __init__(self, title, docstr):
        ida_kernwin.Form.__init__(self,
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
class ChooserData:
    """Structure that holds information for the chooser to display."""
    icon_ids = {"str": 80,
    "int": 8,
    "class": 89,
    "function": 81,
    "method": 99}
    def __init__(self, mod_name, sym_name, file_name):
        self.mod_name = mod_name
        self.sym_name = sym_name
        self.file_name = file_name
        self.doc_str = ""
        self.sym_type = ""
        self.sym_value = ""
        self.line_no = ""

    def get_icon(self):
        return self.icon_ids[self.sym_type]

# --------------------------------------------------------------------------
class PyHelperChooser(ida_kernwin.Choose):
    """A chooser filled with information about IDAPython bindings.
    Output is supposed to be filtered with Ctrl-F."""
    def __init__(self, title, nb=5):
        ida_kernwin.Choose.__init__(self,
                        title,
                        [ ["Module", 10 | ida_kernwin.Choose.CHCOL_PLAIN],
                        ["Symbol", 20 | ida_kernwin.Choose.CHCOL_PLAIN],
                        ["Documentation", 10 | ida_kernwin.Choose.CHCOL_PLAIN],
                        ["Type", 10 | ida_kernwin.Choose.CHCOL_PLAIN],
                        ["Value", 10 | ida_kernwin.Choose.CHCOL_HEX],
                        ["Line number", 10 | ida_kernwin.Choose.CHCOL_DEC],],
                        flags=ida_kernwin.Choose.CH_QFLT | ida_kernwin.Choose.CH_NOIDB)
        self.items = []
        self.icon = 0
        self.build_items()

    def build_items(self):
        subdir = ""
        if is_ida_version(740):
            subdir, _, _, _, _ = sys.version_info
        pydir = ida_diskio.idadir(os.path.join("python", str(subdir)))
        for mod_name in os.listdir(pydir):
            if mod_name.endswith(".py"):
                mod_name, _ = os.path.splitext(mod_name)
                if mod_name not in ["init", "idaapi"]:
                    mod = __import__(mod_name)
                    file_name = mod.__file__
                    for sym_name, obj in inspect.getmembers(mod):

                        if inspect.isfunction(obj):
                            data = ChooserData(mod_name, sym_name, file_name)
                            data.sym_type = "function"
                            data.line_no = "%d" % obj.__code__.co_firstlineno
                            data.doc_str = inspect.getdoc(obj)
                            self.items.append(data)

                        elif inspect.isclass(obj):
                            data = ChooserData(mod_name, sym_name, file_name)
                            data.sym_type = "class"
                            data.doc_str = inspect.getdoc(obj)
                            self.items.append(data)

                        elif inspect.ismethod(obj):
                            data = ChooserData(mod_name, sym_name, file_name)
                            data.sym_type = "method"
                            data.line_no = "%d" % obj.im_func.__code__.co_firstlineno
                            data.doc_str = inspect.getdoc(obj)
                            self.items.append(data)

                        elif type(obj) == int:
                            data = ChooserData(mod_name, sym_name, file_name)
                            data.sym_type = "int"
                            data.sym_value = "0x%x" % (obj)
                            self.items.append(data)

                        elif type(obj) == str:
                            data = ChooserData(mod_name, sym_name, file_name)
                            data.sym_type = "str"
                            data.sym_value = str(obj)
                            self.items.append(data)
                        else:
                            if DBG:
                                msg("%s: %s" % (type(obj), sym_name))

    def OnGetLine(self, n):
        data = self.items[n]
        return [data.mod_name,
        data.sym_name,
        "%s" % data.doc_str,
        data.sym_type,
        data.sym_value,
        data.line_no]

    def OnGetIcon(self, n):
        return self.items[n].get_icon()

    def OnGetSize(self):
        return len(self.items)

    def OnSelectLine(self, n):
        data = self.items[n]
        postfix = " (%s)" % data.mod_name if len(data.mod_name) else ""
        if not data.doc_str:
            ida_kernwin.msg("No documentation available for \"%s\"\n" % data.sym_name)
        else:
            f = DocstringViewer("%s%s" % (data.sym_name, postfix), data.doc_str)
            f.modal = False
            f.openform_flags = ida_kernwin.PluginForm.WOPN_TAB
            f, args = f.Compile()
            f.Open()
        return (ida_kernwin.Choose.NOTHING_CHANGED, )

    def OnEditLine(self, n):
        fn = self.items[n].file_name
        if fn:
            # ghetto
            if fn.endswith(".pyc"):
                fn = fn[:-1]
            with open(fn) as fin:
                f = FileViewer("%s" % (os.path.basename(fn)), fin.read())
                f.modal = False
                f.openform_flags = ida_kernwin.PluginForm.WOPN_TAB
                f, args = f.Compile()
                f.Open()
        return (ida_kernwin.Choose.NOTHING_CHANGED, )            

try:
    pyhelper
except:
    pyhelper=PyHelperChooser("IDAPyHelper")
else:
    if DBG:
        del pyhelper
        pyhelper=PyHelperChooser("IDAPyHelper")
pyhelper.Show()
