from pobfuscatory import obfuscator


class File:
    def __init__(self, lines):
        self.i = 0
        self.lines = lines

    def readline(self):
        self.i += 1
        return self.lines[self.i]


def test_scan_import_project_name():
    keys = obfuscator.Keys()
    scan = obfuscator.ScanImport("source", keys)
    line = "from source.package.bar import bar, zoo"
    scan._execute(line, None)
    assert len(keys.import_key) == 0


def test_scan_import_relative():
    keys = obfuscator.Keys()
    scan = obfuscator.ScanImport("source", keys)
    line = "from .package.bar import bar, zoo"
    scan._execute(line, None)
    assert len(keys.import_key) == 0


def test_scan_import_from_os():
    keys = obfuscator.Keys()
    scan = obfuscator.ScanImport("source", keys)
    line = "from os import path"
    scan._execute(line, None)
    assert len(keys.import_key) == 4


def test_scan_import_os():
    keys = obfuscator.Keys()
    scan = obfuscator.ScanImport("source", keys)
    line = "import os"
    scan._execute(line, None)
    assert len(keys.import_key) == 2


def test_scan_import_os_all():
    keys = obfuscator.Keys()
    scan = obfuscator.ScanImport("source", keys)
    line = "import os"
    scan._execute(line, None)
    keys.collect_library_key()
    assert "path" in keys.special_key


def test_scan_import_multiple_line():
    keys = obfuscator.Keys()
    scan = obfuscator.ScanImport("source", keys)
    lines = ["from shutil import (\n", "copy, move,\n", ")\n"]
    scan._execute(lines[0], File(lines))
    keys.collect_library_key()
    assert "copy" in keys.special_key
    assert "move" in keys.special_key


def test_scan_import_in_docs_1():
    keys = obfuscator.Keys()
    scan = obfuscator.ScanImport("source", keys)
    line = "import library and run test"
    scan._execute(line, None)
    assert len(keys.change_keys) == 0
    assert len(keys.import_key) == 0


def test_scan_import_in_docs_2():
    keys = obfuscator.Keys()
    scan = obfuscator.ScanImport("source", keys)
    line = "from :meth:`_make_session_factory`. The result is available as :attr:`session`"
    scan._execute(line, None)
    assert len(keys.change_keys) == 0
    assert len(keys.import_key) == 0


def test_scan_string_dict():
    keys = obfuscator.Keys()
    scan = obfuscator.ScanString("source", keys)
    line = 'd = {"x": x, "y": 3}'
    scan._execute(line, None)
    assert len(keys.special_key) == 2


def test_scan_string_f_string():
    keys = obfuscator.Keys()
    scan = obfuscator.ScanString("source", keys)
    line = 'f"print x4: {x4}, y4: {y4}, z4: {z4}"'
    scan._execute(line, None)
    assert len(keys.special_key) == 7


def test_scan_var():
    keys = obfuscator.Keys()
    scan = obfuscator.ScanPyVar("source", keys)
    line = 're.fullmatch, string=component["kb_model"]'
    scan._execute(line, None)
    assert len(keys.change_keys) == 0


def test_scan_class_statement():
    keys = obfuscator.Keys()
    scan = obfuscator.ScanPyClass("source", keys)
    line = 'classes_in_img = list(set(bboxes[:, 5]))'
    scan._execute(line, None)
    assert len(keys.change_keys) == 0
