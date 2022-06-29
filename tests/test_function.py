import os
import pytest
import inspect
from shutil import rmtree
from importlib.machinery import SourceFileLoader

from pyobfuscator import obfuscator
from source import function


@pytest.fixture(autouse=True)
def run_around_tests():
    yield
    rmtree("generated")


def test_function():
    ori = function.add(2, 3)
    ori_path = os.path.abspath(inspect.getfile(function))
    obfuscator.obfuscator('source', ori_path)
    generated_func = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfuscator.mapping_table["add"])(2, 3)
    assert ori == result
