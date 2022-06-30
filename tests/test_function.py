import os
import pytest
import shutil
import inspect
from importlib.machinery import SourceFileLoader

from pyobfuscator import obfuscator
from pyobfuscator.obfuscator import Obfuscator, clean_empty_folder
from source import function
from source.package import foo


@pytest.fixture(autouse=True)
def run_around_tests():
    yield
    shutil.rmtree("generated")


def test_function():
    ori_result = function.add(2, 3)
    ori_path = os.path.abspath(inspect.getfile(function))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfuscator.mapping_table["add"])(2, 3)
    assert result == ori_result


def test_package():
    ori_result = foo.foo(1, 2, 3)
    ori_path = os.path.abspath(inspect.getfile(foo))
    obfus = Obfuscator('source', "source", "generated")
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfuscator.mapping_table["foo"])(1, 2, 3)
    assert result == ori_result
    assert len(list(os.walk("generated"))) == 3


def test_clean_empty_folder():
    root = "generated/A"
    os.makedirs("generated/A/b/bb/c")
    os.makedirs("generated/A/a/aa")
    with open("generated/A/b/test.txt", 'w') as f:
        f.write(" ")
    assert len(list(os.walk(root))) == 6
    clean_empty_folder(root)
    assert len(list(os.walk(root))) == 2
