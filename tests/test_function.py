import os
import pytest
import shutil
import inspect
from importlib.machinery import SourceFileLoader

from pyobfuscator import obfuscator
from pyobfuscator.obfuscator import Obfuscator, clean_empty_folder
from source import function
from source.package import foo
from source.classes import A, B, C
from source.comment import comment
from source.multi_comment import multi_comment
from source import special_arg, imports


@pytest.fixture(autouse=True)
def run_around_tests():
    obfuscator.mapping_table = {"source": "generated"}
    obfuscator.unique_str = set()
    obfuscator.test_path_map = {}
    yield
    shutil.rmtree("tests/generated")


def test_function():
    ori_result = function.add(2, 3)
    ori_path = os.path.abspath(inspect.getfile(function))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfuscator.mapping_table["add"])(2, 3)
    assert result == ori_result


def test_multi_line_args():
    ori_result = function.multiply(3, 3)
    ori_path = os.path.abspath(inspect.getfile(function))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfuscator.mapping_table["multiply"])(3, 3)
    assert result == ori_result


def test_assign_value_to_list():
    ori_result = function.assign_value_to_list(1)
    ori_path = os.path.abspath(inspect.getfile(function))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfuscator.mapping_table["assign_value_to_list"])(1)
    assert result == ori_result


def test_assign_value_to_matrix():
    ori_result = function.assign_value_to_matrix(1, 2)
    ori_path = os.path.abspath(inspect.getfile(function))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfuscator.mapping_table["assign_value_to_matrix"])(1, 2)
    assert result == ori_result


def test_parse_string():
    ori_result = function.string(1, 2)
    ori_path = os.path.abspath(inspect.getfile(function))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfuscator.mapping_table["string"])(1, 2)
    assert result == ori_result


def test_parse_multiline_string():
    ori_result = function.multiline_string(1)
    ori_path = os.path.abspath(inspect.getfile(function))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfuscator.mapping_table["multiline_string"])(1)
    assert result == ori_result


def test_package():
    ori_result = foo.foo(1, 2, 3)
    ori_path = os.path.abspath(inspect.getfile(foo))
    obfus = Obfuscator('source', os.path.join("tests", "source", "package"), "generated")
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfuscator.mapping_table["foo"])(1, 2, 3)
    assert result == ori_result
    assert len(list(os.walk("tests/generated"))) == 4


def test_clean_empty_folder():
    root = "tests/generated/A"
    os.makedirs("tests/generated/A/b/bb/c")
    os.makedirs("tests/generated/A/a/aa")
    with open("tests/generated/A/b/test.txt", 'w') as f:
        f.write(" ")
    assert len(list(os.walk(root))) == 6
    clean_empty_folder(root)
    assert len(list(os.walk(root))) == 2


def test_class():
    a = A(2, 3)
    ori_result = a.add()
    ori_path = os.path.abspath(inspect.getfile(A))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_cls = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    cls = getattr(generated_cls, obfuscator.mapping_table["A"])(2, 3)
    result = getattr(cls, obfuscator.mapping_table["add"])()
    assert result == ori_result


def test_inherit_class():
    b = B(1, 2, 3)
    ori_result = b.add()
    ori_path = os.path.abspath(inspect.getfile(B))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_cls = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    cls = getattr(generated_cls, obfuscator.mapping_table["B"])(1, 2, 3)
    result = getattr(cls, obfuscator.mapping_table["add"])()
    assert result == ori_result


def test_class_multi_line_args():
    a = C(2, 3)
    ori_result = a.multiply()
    ori_path = os.path.abspath(inspect.getfile(C))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_cls = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    cls = getattr(generated_cls, obfuscator.mapping_table["C"])(2, 3)
    result = getattr(cls, obfuscator.mapping_table["multiply"])()
    assert result == ori_result


def test_remove_comment():
    ori_path = os.path.abspath(inspect.getfile(comment))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    with open(obfuscator.test_path_map[ori_path], 'r') as f:
        assert len(f.readlines()) == 5


def test_remove_multi_comment():
    ori_path = os.path.abspath(inspect.getfile(multi_comment))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    with open(obfuscator.test_path_map[ori_path], 'r') as f:
        assert len(f.readlines()) == 4


def test_pycache_handle():
    obfus = Obfuscator('source', os.path.join("tests", "source", "pycache"), "generated")
    obfus.obfuscate()
    os.makedirs("tests/generated", exist_ok=True)
    assert os.path.exists("tests/generated/pycache/__pycache__") is True


def test_preserve_function_name():
    ori_result = foo.foo(1, 2, 3)
    ori_path = os.path.abspath(inspect.getfile(foo))
    obfus = Obfuscator('source', os.path.join("tests", "source", "package"), "generated", ["foo"])
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, "foo")(1, 2, 3)
    assert result == ori_result
    assert len(list(os.walk("tests/generated"))) == 4
    assert any(["foo.py" in d[-1] for d in list(os.walk("tests/generated"))])


def test_equal_inline():
    ori_result = special_arg.equal_inline(2, 3)
    ori_path = os.path.abspath(inspect.getfile(special_arg))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfuscator.mapping_table["equal_inline"])(2, 3)
    assert result == ori_result


def test_unpack_list():
    ori_result = special_arg.unpack_list()
    ori_path = os.path.abspath(inspect.getfile(special_arg))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfuscator.mapping_table["unpack_list"])()
    assert result == ori_result


def test_dynamic_args():
    args = [1, 2]
    kwargs = {"x": 1, "y": 2}
    ori_result = special_arg.dynamic_args(*args, **kwargs)
    ori_path = os.path.abspath(inspect.getfile(special_arg))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfuscator.mapping_table["dynamic_args"])(*args, **kwargs)
    assert result == ori_result


def test_import_serial():
    ori_result = imports.concat_path("x", "y")
    ori_path = os.path.abspath(inspect.getfile(imports))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfuscator.mapping_table["concat_path"])("x", "y")
    assert result == ori_result


def test_from_import():
    ori_result = imports.listdir("src")
    ori_path = os.path.abspath(inspect.getfile(imports))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfuscator.mapping_table["list_dir"])("src")
    assert result == ori_result


def test_name_conflict():
    ori_result = imports.name_conflict(1)
    ori_path = os.path.abspath(inspect.getfile(imports))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfuscator.mapping_table["name_conflict"])(1)
    assert result == ori_result


def test_assign_library():
    ori_result = imports.assign_library("x")
    ori_path = os.path.abspath(inspect.getfile(imports))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfuscator.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfuscator.mapping_table["assign_library"])("x")
    assert result == ori_result
