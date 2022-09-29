import inspect
import os
import re
import shutil
import random
import string
import logging
from collections import deque


def generate_random_string(string_list=string.ascii_uppercase, start=4, end=16):
    return "".join(
        random.choice(string_list) for _ in range(random.randint(start, end))
    )


def collect_keyword(extras=None):
    seen = set()
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
    if extras is not None:
        for extra in extras:
            try:
                queue.append((extra, eval(extra)))
            except (NameError, SyntaxError):
                pass
    while queue:
        key, obj = queue.popleft()
        if key not in seen:
            seen.add(key)
            for k, f in inspect.getmembers(obj):
                if (
                    not k.startswith("_") and k not in seen
                ):  # and (inspect.isfunction(f) or inspect.ismodule(f)):
                    queue.append((k, f))
    return seen


class Keys:
    def __init__(self):
        self.mapping_table = {"source": "generated"}
        self.unique_str = set()
        self.test_path_map = {}

        self.change_keys = set()
        self.import_key = set()
        self.special_key = set()

    def init(self, exclude_keys, target):
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
        }

        # add exclude keys
        if isinstance(exclude_keys, (list, tuple)):
            for key in exclude_keys:
                self.special_key.add(key)
        for key in os.path.normpath(target).split(os.sep):
            self.special_key.add(key)

    def collect_library_key(self):
        # collect library keyword
        keyword = collect_keyword(self.import_key)
        self.special_key.update(keyword)

    def update_mapping_table(self):
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
    def __init__(self, args):
        self.source = os.path.normpath(args.source)
        self.target = os.path.normpath(args.target)
        self.keys = Keys()
        self.root = os.path.basename(os.path.dirname(self.source))
        self.keys.init(args.exclude_keys, self.target)
        self.probability = args.probability
        self.repeat = args.repeat

    def obfuscate(self):
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
            self.source = os.path.join(self.target, *sp[sp.index(self.root) + 1 :])
        clean_empty_folder(self.source)

    def _process(self, func):
        if self.source.endswith(".py"):
            file_dir = self.source
            func(file_dir)
        else:
            for root, dirs, files in os.walk(self.source):
                for filename in files:
                    file_dir = os.path.join(root, filename)
                    func(file_dir)


class Scan:
    def __init__(self, project, keys):
        self.project = project
        self.keys = keys

    def _scan_external(self, file_dir):
        split_path = file_dir.split(os.sep)
        filename = os.path.splitext(split_path.pop())[0]
        try:
            modules = split_path[split_path.index(self.project) + 1 :]
            for module in modules + [filename]:
                self.keys.change_keys.add(module)
        except ValueError:
            pass

    def run(self, file_dir):
        if file_dir.endswith(".py"):
            self._scan_external(file_dir)

            with open(file_dir, "r", encoding="utf-8") as f:
                line = f.readline()
                while line:
                    logging.info(f"{file_dir}, {line}")
                    for subclass in Scan.__subclasses__():
                        subclass(self.project, self.keys)._execute(line, f)
                    line = f.readline()

    def _execute(self, line, f):
        raise NotImplementedError


class ScanPyFunc(Scan):
    def _execute(self, line, f):
        line = line.replace(" ", "")
        if line.startswith("def"):
            func = line[3:]
            pare_start = func.index("(")
            func_name = func[:pare_start]
            self.keys.change_keys.add(func_name)

            try:
                pare_end = func.index(")")
                for arg in func[pare_start + 1 : pare_end].split(","):
                    self.keys.change_keys.add(arg.split("=")[0].strip())
            except ValueError:
                while not func.strip().endswith("):"):
                    for arg in func[pare_start + 1 :].split(","):
                        self.keys.change_keys.add(arg.split("=")[0].strip())
                    pare_start = -1
                    func = f.readline().replace(" ", "")
                for arg in func[:-2].split(","):
                    self.keys.change_keys.add(arg.split("=")[0].strip())


class ScanPyVar(Scan):
    def _execute(self, line, f):
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
    def _is_equal_in_parentheses(line):
        if "(" in line and line.index("(") < line.index("="):
            return True
        return False


class ScanPyClass(Scan):
    def _execute(self, line, f):
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
    def _execute(self, line, f):
        line = line.strip()
        # get library name
        line_split = line.split()
        if line_split and line_split[0] in ("import", "from"):
            if line_split[1].startswith(".") or line_split[1].startswith(self.project):
                return
            all_words = re.findall(r"(\w+)", line)
            for w in all_words:
                self.keys.special_key.add(w)
                self.keys.import_key.add(w)
            if not line_split[1].startswith("."):
                exec(line)


class ScanString(Scan):
    def _execute(self, line, f):
        line = line.strip()
        strings = re.findall(r'"(.+?)"', line) + re.findall(r"'(.+?)'", line)
        for s in strings:
            for w in re.findall(r"(?!{)(\w+)(?!})", s):
                self.keys.special_key.add(w)


def convert(file_dir, root, keys, target=None, probability=1, repeat=1):
    target_dir = file_dir
    if target:
        sp = file_dir.split(os.sep)
        target_dir = os.path.join(target, *sp[sp.index(root) + 1 :])

    folder = f"{os.sep}".join(target_dir.split(os.sep)[:-1])
    os.makedirs(folder, exist_ok=True)
    if file_dir.endswith(".py"):
        lines = replace(file_dir, keys, probability, repeat)
        with open(target_dir, "w", encoding="utf-8") as f:
            f.writelines(lines)
    else:
        try:
            shutil.copy(file_dir, target_dir)
        except shutil.SameFileError:
            pass
    rename_file(file_dir, target_dir, keys)


def get_last_bracket_index(i, lines, stack, pattern, sign):
    brackets = re.findall(pattern, lines[i])
    for b in brackets:
        if b == sign:
            stack.append(b)
        else:
            try:
                stack.pop()
            except IndexError:
                return i

    while stack:
        i += 1
        brackets = re.findall(pattern, lines[i])
        for b in brackets:
            if b == sign:
                stack.append(b)
            else:
                stack.pop()
    return i


def generate_confuse_line(i, lines, cache, stack, probability=1, repeat=1):
    try:
        # pass line can not insert confuse string
        pattern = r"\(|\)"
        if re.findall(pattern, lines[i]):
            i = get_last_bracket_index(i, lines, stack, pattern, "(")
            last = re.findall(pattern, lines[i])
            if lines[i].strip().startswith("def") or last[0] == ")":
                return i
        pattern = r"\{|\}"
        if re.findall(pattern, lines[i]):
            i = get_last_bracket_index(i, lines, stack, pattern, "{")
            last = re.findall(pattern, lines[i])
            if last[0] == "}":
                return i
        pattern = r"\[|\]"
        if re.findall(pattern, lines[i]):
            i = get_last_bracket_index(i, lines, stack, pattern, "[")
            last = re.findall(pattern, lines[i])
            if last[0] == "]":
                return i
        if i >= len(lines):
            return i
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


def insert_confuse_line(lines, cache):
    cnt = 0
    for i, v in cache:
        lines.insert(i + cnt, v)
        cnt += 1
    return lines


def replace(file_dir, keys, probability=1, repeat=1):
    with open(file_dir, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i in range(len(lines)):
        replace_keys(i, lines, keys)
        remove_single_comment(i, lines)
        remove_multi_line_comment(i, lines)

    i = 0
    bracket_stack = []
    confuse_cache = []
    while i < len(lines):
        i = generate_confuse_line(
            i, lines, confuse_cache, bracket_stack, probability, repeat
        )
        i += 1
    insert_confuse_line(lines, confuse_cache)

    return lines


def replace_keys(i, lines, keys):
    line = lines[i]
    for k, v in keys.mapping_table.items():
        logging.debug(f"line: {line}, K: {k}, V: {v}")
        line = regex_replace(line, k, v)
        line = line.replace(v + "@", k)  # undo template replace
    lines[i] = line


def remove_single_comment(i, lines):
    line = lines[i].strip()
    if line.startswith("#"):
        lines[i] = ""


def remove_multi_line_comment(i, lines):
    line = lines[i].strip()
    if len(line) > 3 and line.startswith('"""') and line.endswith('"""'):
        lines[i] = ""
    elif line.startswith('"""'):
        lines[i] = ""
        while not lines[i].strip().endswith('"""'):
            lines[i] = ""
            i += 1
        lines[i] = ""


def regex_replace(line, source, target):
    return re.sub(rf"\b{source}\b", target, line)


def rename_file(file_dir, target_dir, keys):
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
    keys.test_path_map.update(
        {os.path.abspath(file_dir): os.path.abspath(obfuscate_dir)}
    )


def clean_empty_folder(root):
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
