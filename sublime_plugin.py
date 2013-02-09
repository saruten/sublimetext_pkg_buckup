import sublime
import threading
import imp
import importlib
import os
import sys
import zipfile
import sublime_api

application_command_classes = []
window_command_classes = []
text_command_classes = []

all_command_classes = [application_command_classes, window_command_classes, text_command_classes]

all_callbacks = {'on_new': [], 'on_clone': [], 'on_load': [], 'on_close': [],
    'on_pre_save': [], 'on_post_save': [], 'on_modified': [],
    'on_selection_modified': [],'on_activated': [], 'on_deactivated': [],
    'on_query_context': [], 'on_query_completions': [],

    'on_modified_async': [],
    'on_selection_modified_async': [],
    'on_pre_save_async': [],
    'on_post_save_async': [],
    'on_activated_async': [],
    'on_deactivated_async': [],
    'on_new_async': [],
    'on_load_async': [],
    'on_clone_async': []}

def unload_module(module):
    if "unload_handler" in module.__dict__:
        module.unload_handler()

    # Unload the old plugins
    if "plugins" in module.__dict__:
        for p in module.plugins:
            for cmd_cls_list in all_command_classes:
                try:
                    cmd_cls_list.remove(p)
                except ValueError:
                    pass
            for c in all_callbacks.values():
                try:
                    c.remove(p)
                except ValueError:
                    pass

def unload_plugin(modulename):
    print("unloading plugin", modulename)

    was_loaded = modulename in sys.modules
    if was_loaded:
        m = sys.modules[modulename]
        unload_module(m)

def reload_plugin(modulename):
    print("reloading plugin", modulename)

    if modulename in sys.modules:
        m = sys.modules[modulename]
        unload_module(m)
        m = imp.reload(m)
    else:
        m = importlib.import_module(modulename)

    module_plugins = []
    for type_name in dir(m):
        try:
            t = m.__dict__[type_name]
            if t.__bases__:
                is_plugin = False
                if issubclass(t, ApplicationCommand):
                    application_command_classes.append(t)
                    is_plugin = True
                if issubclass(t, WindowCommand):
                    window_command_classes.append(t)
                    is_plugin = True
                if issubclass(t, TextCommand):
                    text_command_classes.append(t)
                    is_plugin = True

                if is_plugin:
                    module_plugins.append(t)

                if issubclass(t, EventListener):
                    obj = t()
                    for p in all_callbacks.items():
                        if p[0] in dir(obj):
                            p[1].append(obj)

                    module_plugins.append(obj)

        except AttributeError:
            pass

    if len(module_plugins) > 0:
        m.plugins = module_plugins

def create_application_commands():
    cmds = []
    for class_ in application_command_classes:
        cmds.append(class_())
    sublime_api.notify_application_commands(cmds)

def create_window_commands(window_id):
    window = sublime.Window(window_id)
    cmds = []
    for class_ in window_command_classes:
        cmds.append(class_(window))
    return cmds

def create_text_commands(view_id):
    view = sublime.View(view_id)
    cmds = []
    for class_ in text_command_classes:
        cmds.append(class_(view))
    return cmds

def on_new(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_new']:
        callback.on_new(v)

def on_new_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_new']:
        callback.on_new_async(v)

def on_clone(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_clone']:
        callback.on_clone(v)

def on_clone_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_clone_async']:
        callback.on_clone_async(v)

def on_load(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_load']:
        callback.on_load(v)

def on_load_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_load_async']:
        callback.on_load_async(v)

def on_close(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_close']:
        callback.on_close(v)

def on_pre_save(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_pre_save']:
        callback.on_pre_save(v)

def on_pre_save_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_pre_save_async']:
        callback.on_pre_save_async(v)

def on_post_save(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_post_save']:
        callback.on_post_save(v)

def on_post_save_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_post_save_async']:
        callback.on_post_save_async(v)

def on_modified(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_modified']:
        callback.on_modified(v)

def on_modified_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_modified_async']:
        callback.on_modified_async(v)

def on_selection_modified(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_selection_modified']:
        callback.on_selection_modified(v)

def on_selection_modified_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_selection_modified_async']:
        callback.on_selection_modified_async(v)

def on_activated(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_activated']:
        callback.on_activated(v)

def on_activated_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_activated_async']:
        callback.on_activated_async(v)

def on_deactivated(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_deactivated']:
        callback.on_deactivated(v)

def on_deactivated_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_deactivated_async']:
        callback.on_deactivated_async(v)

def on_query_context(view_id, key, operator, operand, match_all):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_query_context']:
        val = callback.on_query_context(v, key, operator, operand, match_all)
        if val:
            return True

    return False

def normalise_completion(c):
    if len(c) == 1:
        return (c[0], "", "")
    elif len(c) == 2:
        return (c[0], "", c[1])
    else:
        return c

def on_query_completions(view_id, prefix, locations):
    v = sublime.View(view_id)

    completions = []
    flags = 0
    for callback in all_callbacks['on_query_completions']:
        res = callback.on_query_completions(v, prefix, locations)

        if isinstance(res, tuple):
            completions += [normalise_completion(c) for c in res[0]]
            flags |= res[1]
        elif isinstance(res, list):
            completions += [normalise_completion(c) for c in res]

    return (completions,flags)

class Command(object):
    def name(self):
        clsname = self.__class__.__name__
        name = clsname[0].lower()
        last_upper = False
        for c in clsname[1:]:
            if c.isupper() and not last_upper:
                name += '_'
                name += c.lower()
            else:
                name += c
            last_upper = c.isupper()
        if name.endswith("_command"):
            name = name[0:-8]
        return name

    def is_enabled_(self, args):
        ret = None
        try:
            if args:
                if 'event' in args:
                    del args['event']

                ret = self.is_enabled(**args)
            else:
                ret = self.is_enabled()
        except TypeError:
            ret = self.is_enabled()

        if not isinstance(ret, bool):
            raise ValueError("is_enabled must return a bool", self)

        return ret

    def is_enabled(self):
        return True

    def is_visible_(self, args):
        ret = None
        try:
            if args:
                ret = self.is_visible(**args)
            else:
                ret = self.is_visible()
        except TypeError:
            ret = self.is_visible()

        if not isinstance(ret, bool):
            raise ValueError("is_visible must return a bool", self)

        return ret

    def is_visible(self):
        return True

    def is_checked_(self, args):
        ret = None
        try:
            if args:
                ret = self.is_checked(**args)
            else:
                ret = self.is_checked()
        except TypeError:
            ret = self.is_checked()

        if not isinstance(ret, bool):
            raise ValueError("is_checked must return a bool", self)

        return ret

    def is_checked(self):
        return False

    def description_(self, args):
        try:
            if args != None:
                return self.description(**args)
            else:
                return self.description()
        except TypeError as e:
            return ""

    def description(self):
        return ""


class ApplicationCommand(Command):
    def run_(self, edit_token, args):
        if args:
            if 'event' in args:
                del args['event']

            return self.run(**args)
        else:
            return self.run()

    def run(self):
        pass


class WindowCommand(Command):
    def __init__(self, window):
        self.window = window

    def run_(self, edit_token, args):
        if args:
            if 'event' in args:
                del args['event']

            return self.run(**args)
        else:
            return self.run()

    def run(self):
        pass


class TextCommand(Command):
    def __init__(self, view):
        self.view = view

    def run_(self, edit_token, args):
        if args:
            if 'event' in args:
                del args['event']

            edit = self.view.begin_edit(edit_token, self.name(), args)
            try:
                return self.run(edit, **args)
            finally:
                self.view.end_edit(edit)
        else:
            edit = self.view.begin_edit(edit_token, self.name())
            try:
                return self.run(edit)
            finally:
                self.view.end_edit(edit)

    def run(self, edit):
        pass


class EventListener(object):
    pass

class MultizipImporter(object):
    def __init__(self):
        self.loaders = []

    def find_module(self, fullname, path = None):
        if not path:
            for l in self.loaders:
                if l.name == fullname:
                    return l;

        for l in self.loaders:
            if path == [l.path]:
                if l.has(fullname):
                    return l

        return None


class ZipLoader(object):
    def __init__(self, path):
        self.path = path
        self.name = os.path.splitext(os.path.basename(path))[0]

        z = zipfile.ZipFile(path, 'r')
        files = [i.filename for i in z.infolist()]

        self.contents = {"":""}

        for f in files:
            base, ext = os.path.splitext(f)
            if ext != ".py":
                continue

            paths = base.split('/')

            self.contents['.'.join(paths)] = z.read(f).decode('utf-8')

            paths.pop()
            while len(paths) > 0:
                self.contents['.'.join(paths)] = ""
                paths.pop()

        z.close()

    def has(self, fullname):
        key = '.'.join(fullname.split('.')[1:])
        return key in self.contents

    def load_module(self, fullname):
        if fullname in sys.modules:
            mod = sys.modules[fullname]
        else:
            mod = sys.modules.setdefault(fullname, imp.new_module(fullname))

        mod.__file__ = self.path + "/" + fullname
        mod.__name__ = fullname
        mod.__path__ = [self.path]
        mod.__loader__ = self
        mod.__package__ = '.'.join(fullname.split('.')[:-1])

        key = '.'.join(fullname.split('.')[1:])
        source = self.contents[key]

        if source == None:
            file = '/'.join(fullname.split('.')[1:])

        exec(source, mod.__dict__)
        return mod

multi_importer = MultizipImporter()
sys.meta_path.append(multi_importer)

def update_compressed_packages(pkgs):
    multi_importer.loaders = [ZipLoader(p) for p in pkgs]
