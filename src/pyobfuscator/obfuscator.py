import inspect
import os
import re
import shutil
import random
import string
import logging
from collections import deque
from typing import IO


def generate_random_string(
    strings: str = string.ascii_uppercase, minimum: int = 4, maximum: int = 16
) -> str:
    """Generate random string.

    Args:
        strings: This strings must fits rules for python variables.
        minimum: Minimum length of random string.
        maximum: Maximum length of random string.

    Returns:
        The length of random string is between {start} and {end}.
    """
    return "".join(
        random.choice(strings) for _ in range(random.randint(minimum, maximum))
    )


def collect_library_keyword(extras: set = None) -> set:
    """Collect all keywords from other library for preserving the raw name.

    Args:
        extras: The import libraries set.

    Returns:
        The set of import library keywords.
    """
    seen = set()
    # initial queue
    queue = deque(
        [
            ("int", int),
            ("float", float),
            ("bool", bool),
            ("str", str),
            ("dict", dict),
            ("set", set),
            ("list", list),
        ]
    )
    # run the import libraries and add to queue
    if extras is not None:
        for extra in extras:
            try:
                queue.append((extra, eval(extra)))
            except (NameError, SyntaxError):
                pass
    # add key to seen and find other public members
    while queue:
        key, obj = queue.popleft()
        if key not in seen:
            seen.add(key)
            for k, f in inspect.getmembers(obj):
                if not k.startswith("_") and k not in seen:
                    queue.append((k, f))
    return seen


class Keys:
    """Store and process keywords.

    Attributes:
        mapping_table: Raw-random keyword pair for converting code to obfuscated.
        unique_str: Store random keyword, prevent reusing the keyword.
        change_keys: Key will be obfuscate in this set.
        import_key: Import library set from source code.
        special_key: Key in this set will be preserve.
        test_path_map: Source-target path pair for unit test.
    """

    def __init__(self) -> None:
        self.mapping_table = {"source": "generated"}
        self.unique_str = set()

        self.change_keys = set()
        self.import_key = set()
        self.special_key = set()

        self.test_path_map = {}

    def init(self, exclude_keys: list, target: str) -> None:
        """Lazy initialize, add key to special_key set"""
        self.special_key = {
            "__init__",
            "self",
            "",
            "'",
            '"',
            "_",
            "*args",
            "**kwargs",
            "(",
            ")",
            "**args",
            "f",
            "nargs",
        }
        # add exclude keys
        if isinstance(exclude_keys, list):
            for key in exclude_keys:
                self.special_key.add(key)
        # add target folder
        for key in os.path.normpath(target).split(os.sep):
            self.special_key.add(key)

    def collect_library_key(self) -> None:
        keyword = collect_library_keyword(self.import_key)
        self.special_key.update(keyword)

    def update_mapping_table(self) -> None:
        """Update raw-random pair string to mapping_table"""
        for func_name in self.change_keys:
            if (
                func_name not in self.mapping_table
                and func_name not in self.special_key
            ):
                random_string = generate_random_string()
                while random_string in self.unique_str:
                    random_string = generate_random_string()
                self.mapping_table.update({func_name: random_string})
                self.unique_str.add(generate_random_string())


class Obfuscator:
    """Obfuscator class

    This class takes three steps.
    1. scan code from source, and generate random obfuscated keys.
    2. convert source code to target obfuscated code.
    3. remote the empty folder in target.

    Attributes:
        source: Source code path waiting to be obfuscated.
        target: Target path to save obfuscated code.
        keys: Store and process keywords class.
        root: Last folder name of source path.
        probability: Probability of confuse line insertion (between 0.0 ~ 1.0)
        repeat: Maximum confuse line insertion number at same place (greater than 0)
    """

    def __init__(self, args) -> None:
        self.source = os.path.normpath(args.source)
        self.target = os.path.normpath(args.target)
        self.keys = Keys()
        self.root = os.path.basename(os.path.dirname(self.source))
        self.keys.init(args.exclude_keys, self.target)
        self.probability = args.probability
        self.repeat = args.repeat

    def obfuscate(self) -> None:
        scan = Scan(self.root, self.keys)
        # scan all files
        self._process(scan.run)
        self.keys.collect_library_key()
        # generate random word map
        self.keys.update_mapping_table()

        # convert files
        self._process(
            lambda x: convert(
                x,
                root=self.root,
                keys=self.keys,
                target=self.target,
                probability=self.probability,
                repeat=self.repeat,
            )
        )
        if self.target:
            sp = self.source.split(os.sep)
            self.target = os.path.join(self.target, *sp[sp.index(self.root) + 1 :])
        clean_empty_folder(self.target)

    def _process(self, func) -> None:
        if self.source.endswith(".py"):
            file_dir = self.source
            func(file_dir)
        else:
            for root, dirs, files in os.walk(self.source):
                for filename in files:
                    file_dir = os.path.join(root, filename)
                    func(file_dir)


def clean_empty_folder(root: str) -> None:
    folders = list(os.walk(root))
    for folder in folders:
        if folder[0] != root:
            clean_empty_folder(folder[0])
        try:
            os.rmdir(folder[0])
        except OSError:
            pass
    # clean root folder
    if folders:
        try:
            os.rmdir(folders[0][0])
        except (FileNotFoundError, OSError):
            pass


class Scan:
    """Base class of scan file"""
    def __init__(self, root: str, keys: Keys) -> None:
        self.root = root
        self.keys = keys

    def _scan_external(self, file_dir: str) -> None:
        """Get the folder name after the root string, add to change key
        Example:
            root = 'project'
            file_dir = ./test/project/path/test.py
            modules = [path]
        """
        split_path = file_dir.split(os.sep)
        filename = os.path.splitext(split_path.pop())[0]
        try:
            modules = split_path[split_path.index(self.root) + 1:]
            for module in modules + [filename]:
                self.keys.change_keys.add(module)
        except ValueError:
            pass

    def run(self, file_dir: str) -> None:
        """open file and run through sub-class"""
        if file_dir.endswith(".py"):
            self._scan_external(file_dir)

            with open(file_dir, "r", encoding="utf-8") as f:
                line = f.readline()
                while line:
                    logging.debug(f"{file_dir}, {line}")
                    for subclass in Scan.__subclasses__():
                        subclass(self.root, self.keys)._execute(line, f)
                    line = f.readline()

    def _execute(self, line: str, f: IO) -> None:
        raise NotImplementedError


class ScanPyFunc(Scan):
    def _execute(self, line: str, f: IO) -> None:
        """Scan function name and function argument, add to change key."""
        is_def = line.strip().split()
        if is_def and is_def[0] == "def":
            line = line.replace(" ", "")
            func = line[3:]
            pare_start = func.index("(")
            func_name = func[:pare_start]
            self.keys.change_keys.add(func_name)

            try:
                pare_end = func.index(")")
                for arg in func[pare_start + 1 : pare_end].split(","):
                    self.keys.change_keys.add(arg.split("=")[0].strip())
            except ValueError:
                while not func.strip().endswith(":"):
                    for arg in func[pare_start + 1 :].strip().split(","):
                        self.keys.change_keys.add(arg.split("=")[0].strip().split(":")[0])
                    pare_start = -1
                    func = f.readline().replace(" ", "")
                for arg in func[:func.index(")")].split(","):
                    self.keys.change_keys.add(arg.split("=")[0].strip())


class ScanPyVar(Scan):
    def _execute(self, line: str, f: IO) -> None:
        """Scan variable, add to change key."""
        line = line.replace(" ", "")
        if (
            "=" in line
            and not line.startswith("def")
            and not self._is_equal_in_parentheses(line)
            and "." not in line
        ):
            ind = 0
            for k in ("=", "+=", "-=", "/=", "*="):
                try:
                    ind = line.index(k)
                except ValueError:
                    pass

            varstring = line[:ind]
            for c in ("*", "(", ")"):
                varstring = varstring.replace(c, "")
            for var in varstring.split(","):
                if var.startswith("self."):
                    var = var[5:]
                if "[" in var:
                    var = var[: var.index("[")]
                self.keys.change_keys.add(var)

    @staticmethod
    def _is_equal_in_parentheses(line: str) -> bool:
        if "(" in line and line.index("(") < line.index("="):
            return True
        return False


class ScanPyClass(Scan):
    def _execute(self, line: str, f: IO) -> None:
        """Scan class name and class argument, add to change key."""
        line = line.replace(" ", "")
        if line.startswith("class"):
            cls = line.strip()[5:]
            try:
                pare_start, pare_end = cls.index("("), cls.index(")")
                for func_name in cls[pare_start + 1 : pare_end].split(","):
                    self.keys.change_keys.add(func_name)
            except ValueError:
                pare_start, pare_end = -1, -1
            func_name = cls[:pare_start]
            self.keys.change_keys.add(func_name)


class ScanImport(Scan):
    def _execute(self, line: str, f: IO) -> None:
        """Scan import library, add to special and import key."""
        line = line.strip()
        # get library name
        line_split = line.split()
        if line_split and line_split[0] in ("import", "from"):
            if line_split[1].startswith(".") or line_split[1].startswith(self.root):
                return
            all_words = re.findall(r"(\w+)", line)
            for w in all_words:
                self.keys.special_key.add(w)
                self.keys.import_key.add(w)
            if not line_split[1].startswith("."):
                exec(line)


class ScanString(Scan):
    def _execute(self, line: str, f: IO) -> None:
        """Scan string in code, add to special key"""
        line = line.strip()
        strings = re.findall(r'"(.+?)"', line) + re.findall(r"'(.+?)'", line)
        for s in strings:
            for w in re.findall(r"(?!{)(\w+)(?!})", s):
                self.keys.special_key.add(w)


def convert(file_dir: str, root: str, keys: Keys, target: str, probability: float = 1.0, repeat: int = 1) -> None:
    """Convert source code to obfuscated code."""
    target_dir = file_dir
    if target:
        sp = file_dir.split(os.sep)
        target_dir = os.path.join(target, *sp[sp.index(root) + 1 :])

    folder = f"{os.sep}".join(target_dir.split(os.sep)[:-1])
    os.makedirs(folder, exist_ok=True)
    if file_dir.endswith(".py"):
        # change raw key to random key by mapping_table
        lines = replace(file_dir, keys, probability, repeat)
        # save obfuscated file to target_dir
        with open(target_dir, "w", encoding="utf-8") as f:
            f.writelines(lines)
    else:
        try:
            # copy non-py file to target_dir
            shutil.copy(file_dir, target_dir)
        except shutil.SameFileError:
            pass
    # rename raw file name to random name by mapping_table
    rename_file(file_dir, target_dir, keys)


def replace(file_dir: str, keys: Keys, probability: float = 1.0, repeat: int = 1) -> list:
    with open(file_dir, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i in range(len(lines)):
        # replace raw key to random key
        replace_keys(i, lines, keys)

        remove_single_comment(i, lines)
        remove_multi_line_comment(i, lines)

    i = 0
    confuse_cache = []
    while i < len(lines):
        i = generate_confuse_line(
            i, lines, confuse_cache, probability, repeat
        )
        i += 1
    insert_confuse_line(lines, confuse_cache)

    return lines


def replace_keys(i: int, lines: list, keys: Keys) -> None:
    line = lines[i]
    for k, v in keys.mapping_table.items():
        logging.debug(f"line: {line}, K: {k}, V: {v}")
        line = regex_replace(line, k, v)
        line = line.replace(v + "@", k)  # undo template replace
    lines[i] = line


def remove_single_comment(i: int, lines: list) -> None:
    line = lines[i].strip()
    if line.startswith("#"):
        lines[i] = ""


def remove_multi_line_comment(i: int, lines: list) -> None:
    line = lines[i].strip()
    if len(line) > 3 and line.startswith('"""') and line.endswith('"""'):
        lines[i] = ""
    elif line.startswith('"""'):
        lines[i] = ""
        while not lines[i].strip().endswith('"""'):
            lines[i] = ""
            i += 1
        lines[i] = ""


def generate_confuse_line(i: int, lines: list, cache: list, probability: float = 1.0, repeat: int = 1) -> int:
    """Generate confuse line list for inserting at obfuscated code

    Args:
        i: Index of file line.
        lines: File content list.
        cache: Confuse line list.
        probability: Probability of confuse line insertion (between 0.0 ~ 1.0)
        repeat: Maximum confuse line insertion number at same place (greater than 0)

    Returns:
        File line index.
    """
    try:
        # pass line can not insert confuse string.
        # "()" cross multiple line.
        pattern = r"\(|\)"
        if re.findall(pattern, lines[i]):
            i = get_last_bracket_index(i, lines, pattern, "(")
            last = re.findall(pattern, lines[i])
            if lines[i].strip().startswith("def") or last[0] == ")":
                return i
        # "{}" cross multiple line.
        pattern = r"\{|\}"
        if re.findall(pattern, lines[i]):
            i = get_last_bracket_index(i, lines, pattern, "{")
            last = re.findall(pattern, lines[i])
            if last[0] == "}":
                return i
        # "[]" cross multiple line.
        pattern = r"\[|\]"
        if re.findall(pattern, lines[i]):
            i = get_last_bracket_index(i, lines, pattern, "[")
            last = re.findall(pattern, lines[i])
            if last[0] == "]":
                return i
        if i >= len(lines):
            return i
        # special keyword can not insert confuse line above the code.
        bypass = lines[i].strip()
        if (
                bypass == ""
                or bypass.startswith(("'", '"', "elif", "else", "except", "@"))
                or bypass.endswith(("'", '"'))
        ):
            return i

        # generate confuse string
        line = lines[i]
        if random.random() < probability:
            for _ in range(random.randint(1, repeat)):
                space = len(line) - len(line.lstrip()) if line != "\n" else 0
                var = generate_random_string(string.ascii_letters, 5, 20)
                val = f'"{generate_random_string(string.ascii_letters + string.digits, 5, 30)}"'
                res = (i, " " * space + var + " = " + val + "\n")
                cache.append(res)
        return i
    except IndexError:
        return i


def get_last_bracket_index(i: int, lines: list, pattern: str, sign: str) -> int:
    """Get the last index, if bracket cross multiple lines.

    Args:
        i: Index of file line.
        lines: File content list.
        pattern: Regex pattern to get bracket.
        sign: Start symbol, i.e., "(", "{", "[".

    Returns:
        Last index.
    """
    stack = []
    # Find brackets. if brackets close in-line, return index.
    brackets = re.findall(pattern, lines[i])
    for b in brackets:
        if b == sign:
            stack.append(b)
        else:
            try:
                stack.pop()
            except IndexError:
                return i

    # If brackets cross multiple line, then find the last close bracket.
    while stack:
        i += 1
        brackets = re.findall(pattern, lines[i])
        for b in brackets:
            if b == sign:
                stack.append(b)
            else:
                stack.pop()
    return i


def insert_confuse_line(lines: list, cache: list) -> list:
    cnt = 0
    for i, v in cache:
        lines.insert(i + cnt, v)
        cnt += 1
    return lines


def regex_replace(line: str, source: str, target: str) -> str:
    """replace word to target (whole word only and match case)"""
    return re.sub(rf"\b{source}\b", target, line)


def rename_file(file_dir: str, target_dir: str, keys: Keys) -> None:
    obfuscate_dir = target_dir.split(os.sep)
    for i, d in enumerate(obfuscate_dir):
        if d.endswith(".py"):
            d = os.path.splitext(d)[0]
        if d in keys.mapping_table:
            obfuscate_dir[i] = keys.mapping_table[d]
    obfuscate_dir = f"{os.sep}".join(obfuscate_dir)
    if target_dir.endswith(".py"):
        obfuscate_dir = (
            obfuscate_dir if obfuscate_dir.endswith(".py") else obfuscate_dir + ".py"
        )

    folder = f"{os.sep}".join(obfuscate_dir.split(os.sep)[:-1])
    os.makedirs(folder, exist_ok=True)
    os.rename(target_dir, obfuscate_dir)

    # for unit test
    keys.test_path_map.update(
        {os.path.abspath(file_dir): os.path.abspath(obfuscate_dir)}
    )
