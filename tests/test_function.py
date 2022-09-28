import os
import pytest
import shutil
import inspect
from importlib.machinery import SourceFileLoader

from pyobfuscator.obfuscator import Obfuscator, clean_empty_folder
from source.package import foo
from source.classes import A, B, C
from source import function, comment, multi_comment, special_arg, imports, case


@pytest.fixture
def args():
    class args:
        def __init__(self):
            self.source = None
            self.target = "./tests/generated"
            self.exclude_keys = None
            self.probability = 1
            self.repeat = 1

    return args()


def _compare_result(arg, func, *args, **kwargs):
    ori_result = func(*args, **kwargs)
    ori_path = os.path.abspath(inspect.getfile(eval(func.__module__.split(".")[-1])))
    arg.source = ori_path
    obfus = Obfuscator(arg)
    obfus.obfuscate()
    generated_func = SourceFileLoader(
        "", obfus.keys.test_path_map[ori_path]
    ).load_module()
    result = getattr(
        generated_func, obfus.keys.mapping_table.get(func.__name__, func.__name__)
    )(*args, **kwargs)
    assert result == ori_result


@pytest.fixture(autouse=True)
def run_around_tests():
    yield
    shutil.rmtree("tests/generated")


def test_function(args):
    _compare_result(args, function.add, 2, 3)


def test_multi_line_args(args):
    _compare_result(args, function.multiply, 3, 3)


def test_assign_value_to_list(args):
    _compare_result(args, function.assign_value_to_list, 1)


def test_assign_value_to_matrix(args):
    _compare_result(args, function.assign_value_to_matrix, 1, 2)


def test_parse_string(args):
    _compare_result(args, function.string, 1, 2)


def test_parse_multiline_string(args):
    _compare_result(args, function.multiline_string, 1)


def test_package(args):
    ori_result = foo.foo(1, 2, 3)
    ori_path = os.path.abspath(inspect.getfile(foo))
    args.source = os.path.join("tests", "source", "package")
    obfus = Obfuscator(args)
    obfus.obfuscate()
    generated_func = SourceFileLoader(
        "", obfus.keys.test_path_map[ori_path]
    ).load_module()
    result = getattr(generated_func, obfus.keys.mapping_table["foo"])(1, 2, 3)
    assert result == ori_result
    assert len(list(os.walk("tests/generated"))) == 4


def test_clean_empty_folder():
    root = "tests/generated/A"
    os.makedirs("tests/generated/A/b/bb/c")
    os.makedirs("tests/generated/A/a/aa")
    with open("tests/generated/A/b/test.txt", "w") as f:
        f.write(" ")
    assert len(list(os.walk(root))) == 6
    clean_empty_folder(root)
    assert len(list(os.walk(root))) == 2


def test_class(args):
    a = A(2, 3)
    ori_result = a.add()
    ori_path = os.path.abspath(inspect.getfile(A))
    args.source = ori_path
    obfus = Obfuscator(args)
    obfus.obfuscate()
    generated_cls = SourceFileLoader(
        "", obfus.keys.test_path_map[ori_path]
    ).load_module()
    cls = getattr(generated_cls, obfus.keys.mapping_table["A"])(2, 3)
    result = getattr(cls, obfus.keys.mapping_table.get("add", "add"))()
    assert result == ori_result


def test_inherit_class(args):
    b = B(1, 2, 3)
    ori_result = b.add()
    ori_path = os.path.abspath(inspect.getfile(B))
    args.source = ori_path
    obfus = Obfuscator(args)
    obfus.obfuscate()
    generated_cls = SourceFileLoader(
        "", obfus.keys.test_path_map[ori_path]
    ).load_module()
    cls = getattr(generated_cls, obfus.keys.mapping_table["B"])(1, 2, 3)
    result = getattr(cls, obfus.keys.mapping_table.get("add", "add"))()
    assert result == ori_result


def test_class_multi_line_args(args):
    a = C(2, 3)
    ori_result = a.multiply()
    ori_path = os.path.abspath(inspect.getfile(C))
    args.source = ori_path
    obfus = Obfuscator(args)
    obfus.obfuscate()
    generated_cls = SourceFileLoader(
        "", obfus.keys.test_path_map[ori_path]
    ).load_module()
    cls = getattr(generated_cls, obfus.keys.mapping_table["C"])(2, 3)
    result = getattr(cls, obfus.keys.mapping_table["multiply"])()
    assert result == ori_result


def test_remove_comment(args):
    ori_path = os.path.abspath(inspect.getfile(comment))
    args.source = ori_path
    obfus = Obfuscator(args)
    obfus.obfuscate()
    with open(obfus.keys.test_path_map[ori_path], "r") as f:
        assert len(f.readlines()) == 3


def test_remove_multi_comment(args):
    ori_path = os.path.abspath(inspect.getfile(multi_comment))
    args.source = ori_path
    obfus = Obfuscator(args)
    obfus.obfuscate()
    with open(obfus.keys.test_path_map[ori_path], "r") as f:
        assert len(f.readlines()) == 3


def test_pycache_handle(args):
    args.source = os.path.join("tests", "source", "pycache")
    obfus = Obfuscator(args)
    obfus.obfuscate()
    os.makedirs("tests/generated", exist_ok=True)
    assert os.path.exists("tests/generated/pycache/__pycache__") is True


def test_preserve_function_name(args):
    ori_result = foo.foo(1, 2, 3)
    ori_path = os.path.abspath(inspect.getfile(foo))
    args.source = os.path.join("tests", "source", "package")
    args.exclude_keys = ["foo"]
    obfus = Obfuscator(args)
    obfus.obfuscate()
    generated_func = SourceFileLoader(
        "", obfus.keys.test_path_map[ori_path]
    ).load_module()
    result = getattr(generated_func, "foo")(1, 2, 3)
    assert result == ori_result
    assert len(list(os.walk("tests/generated"))) == 4
    assert any(["foo.py" in d[-1] for d in list(os.walk("tests/generated"))])


def test_equal_inline(args):
    _compare_result(args, special_arg.equal_inline, 2, 3)


def test_unpack_list(args):
    _compare_result(args, special_arg.unpack_list)


def test_dynamic_args(args):
    value = [1, 2]
    kwargs = {"x": 1, "y": 2}
    ori_result = special_arg.dynamic_args(*value, **kwargs)
    ori_path = os.path.abspath(inspect.getfile(special_arg))
    args.source = ori_path
    obfus = Obfuscator(args)
    obfus.obfuscate()
    generated_func = SourceFileLoader(
        "", obfus.keys.test_path_map[ori_path]
    ).load_module()
    result = getattr(generated_func, obfus.keys.mapping_table["dynamic_args"])(
        *value, **kwargs
    )
    assert result == ori_result


def test_import_serial(args):
    _compare_result(args, imports.concat_path, "x", "y")


def test_from_import(args):
    _compare_result(args, imports.from_import, "src")


def test_name_conflict(args):
    _compare_result(args, imports.name_conflict, 1)


def test_assign_library(args):
    _compare_result(args, imports.assign_library, "x")


def test_get_dict_value(args):
    _compare_result(args, function.get_dict_value, "x")


def test_dict_add(args):
    _compare_result(args, function.dict_add, 3)


def test_log(args):
    _compare_result(args, case.log)


def test_startswith(args):
    _compare_result(args, case.startswith, "test")


def test_multiline_list(args):
    _compare_result(args, case.multiline_list, 1, 2, 3)
