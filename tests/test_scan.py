from pobfuscatory import obfuscator


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
