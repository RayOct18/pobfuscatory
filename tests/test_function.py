import os
import pytest
import shutil
import inspect
from importlib.machinery import SourceFileLoader

from pyobfuscator import obfuscator
from pyobfuscator.obfuscator import Obfuscator, clean_empty_folder
from source.package import foo
from source.classes import A, B, C
from source import function, comment, multi_comment, special_arg, imports


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    obfuscator.mapping_table = {"source": "generated"}
    obfuscator.unique_str = set()
    obfuscator.test_path_map = {}
    yield


def _compare_result(func, *args, **kwargs):
    ori_result = func(*args, **kwargs)
    ori_path = os.path.abspath(inspect.getfile(eval(func.__module__.split(".")[-1])))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfus.keys.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfus.keys.mapping_table.get(func.__name__, func.__name__))(*args, **kwargs)
    assert result == ori_result


@pytest.fixture(autouse=True)
def run_around_tests():
    obfuscator.mapping_table = {"source": "generated"}
    obfuscator.unique_str = set()
    obfuscator.test_path_map = {}
    yield
    shutil.rmtree("tests/generated")


def test_function():
    _compare_result(function.add, 2, 3)


def test_multi_line_args():
    _compare_result(function.multiply, 3, 3)


def test_assign_value_to_list():
    _compare_result(function.assign_value_to_list, 1)


def test_assign_value_to_matrix():
    _compare_result(function.assign_value_to_matrix, 1, 2)


def test_parse_string():
    _compare_result(function.string, 1, 2)


def test_parse_multiline_string():
    _compare_result(function.multiline_string, 1)


def test_package():
    ori_result = foo.foo(1, 2, 3)
    ori_path = os.path.abspath(inspect.getfile(foo))
    obfus = Obfuscator('source', os.path.join("tests", "source", "package"), "generated")
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfus.keys.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfus.keys.mapping_table["foo"])(1, 2, 3)
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
    generated_cls = SourceFileLoader("", obfus.keys.test_path_map[ori_path]).load_module()
    cls = getattr(generated_cls, obfus.keys.mapping_table["A"])(2, 3)
    result = getattr(cls, obfus.keys.mapping_table.get("add", "add"))()
    assert result == ori_result


def test_inherit_class():
    b = B(1, 2, 3)
    ori_result = b.add()
    ori_path = os.path.abspath(inspect.getfile(B))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_cls = SourceFileLoader("", obfus.keys.test_path_map[ori_path]).load_module()
    cls = getattr(generated_cls, obfus.keys.mapping_table["B"])(1, 2, 3)
    result = getattr(cls, obfus.keys.mapping_table.get("add", "add"))()
    assert result == ori_result


def test_class_multi_line_args():
    a = C(2, 3)
    ori_result = a.multiply()
    ori_path = os.path.abspath(inspect.getfile(C))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_cls = SourceFileLoader("", obfus.keys.test_path_map[ori_path]).load_module()
    cls = getattr(generated_cls, obfus.keys.mapping_table["C"])(2, 3)
    result = getattr(cls, obfus.keys.mapping_table["multiply"])()
    assert result == ori_result


def test_remove_comment():
    ori_path = os.path.abspath(inspect.getfile(comment))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    with open(obfus.keys.test_path_map[ori_path], 'r') as f:
        assert len(f.readlines()) == 4


def test_remove_multi_comment():
    ori_path = os.path.abspath(inspect.getfile(multi_comment))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    with open(obfus.keys.test_path_map[ori_path], 'r') as f:
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
    generated_func = SourceFileLoader("", obfus.keys.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, "foo")(1, 2, 3)
    assert result == ori_result
    assert len(list(os.walk("tests/generated"))) == 4
    assert any(["foo.py" in d[-1] for d in list(os.walk("tests/generated"))])


def test_equal_inline():
    _compare_result(special_arg.equal_inline, 2, 3)


def test_unpack_list():
    _compare_result(special_arg.unpack_list)


def test_dynamic_args():
    args = [1, 2]
    kwargs = {"x": 1, "y": 2}
    ori_result = special_arg.dynamic_args(*args, **kwargs)
    ori_path = os.path.abspath(inspect.getfile(special_arg))
    obfus = Obfuscator('source', ori_path, 'generated')
    obfus.obfuscate()
    generated_func = SourceFileLoader("", obfus.keys.test_path_map[ori_path]).load_module()
    result = getattr(generated_func, obfus.keys.mapping_table["dynamic_args"])(*args, **kwargs)
    assert result == ori_result


def test_import_serial():
    _compare_result(imports.concat_path, "x", "y")


def test_from_import():
    _compare_result(imports.from_import, "src")


def test_name_conflict():
    _compare_result(imports.name_conflict, 1)


def test_assign_library():
    _compare_result(imports.assign_library, "x")


def test_get_dict_value():
    _compare_result(function.get_dict_value, "x")


def test_dict_add():
    _compare_result(function.dict_add, 3)
