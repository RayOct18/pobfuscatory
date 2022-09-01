import os
import re
import shutil
import random
import string
import logging

mapping_table = {"source": "generated"}
unique_str = set()
test_path_map = {}


def generate_random_string():
    return ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(3, 10)))


class Obfuscator:
    def __init__(self, project, path, target=None, exclude_keys=None):
        self.project = project
        self.path = path
        self.target = target
        self.exclude_keys = exclude_keys

    def obfuscate(self):
        self._scan()
        self._convert()
        if self.target:
            self.path = self.path.replace(self.project, self.target)
        clean_empty_folder(self.path)

    def _process_file(self, func):
        if self.path.endswith(".py"):
            file_dir = self.path
            func(file_dir)
        else:
            for root, dirs, files in os.walk(self.path):
                for filename in files:
                    file_dir = os.path.join(root, filename)
                    func(file_dir)

    def _scan(self):
        self._process_file(Scan(self.project, exclude_keys=self.exclude_keys).run)

    def _convert(self):
        self._process_file(lambda x: convert(x, project=self.project, target=self.target))


class Scan:
    keys = set()
    import_key = set()
    special_key = {"__init__", "self", "", "'", '"', "_", "*args", "**kwargs", "(", ")", "**args"}

    def __init__(self, project, exclude_keys=None):
        self.project = project
        if isinstance(exclude_keys, (list, tuple)):
            for key in exclude_keys:
                self.special_key.add(key)

    def _scan_external(self, file_dir):
        split_path = file_dir.split(os.sep)
        filename = os.path.splitext(split_path.pop())[0]
        modules = split_path[split_path.index(self.project) + 1:]
        for module in modules + [filename]:
            self.keys.add(module)

    def run(self, file_dir):
        if file_dir.endswith(".py"):
            self._scan_external(file_dir)

            with open(file_dir, 'r', encoding='utf-8') as f:
                line = f.readline()
                while line:
                    logging.info(f"{file_dir}, {line}")
                    for subclass in Scan.__subclasses__():
                        subclass(self.project)._execute(line, f)
                    line = f.readline()

            self._update_mapping_table()

    def _execute(self, line, f):
        raise NotImplementedError

    def _update_mapping_table(self):
        for func_name in self.keys:
            if func_name not in mapping_table and func_name not in self.special_key:
                random_string = generate_random_string()
                while random_string in unique_str:
                    random_string = generate_random_string()
                mapping_table.update({func_name: random_string})
                unique_str.add(generate_random_string())


class ScanPyFunc(Scan):
    def _execute(self, line, f):
        line = line.replace(' ', '')
        if line.startswith("def"):
            func = line[3:]
            pare_start = func.index('(')
            func_name = func[:pare_start]
            self.keys.add(func_name)

            try:
                pare_end = func.index(')')
                for arg in func[pare_start + 1:pare_end].split(','):
                    self.keys.add(arg.split("=")[0].strip())
            except ValueError:
                while not func.strip().endswith("):"):
                    for arg in func[pare_start+1:].split(','):
                        self.keys.add(arg.split("=")[0].strip())
                    pare_start = -1
                    func = f.readline().replace(' ', '')
                for arg in func[:-2].split(','):
                    self.keys.add(arg.split("=")[0].strip())


class ScanPyVar(Scan):
    def _execute(self, line, f):
        line = line.replace(' ', '')
        if "=" in line and not line.startswith("def") and not self._is_equal_in_parentheses(line):
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
                    var = var[:var.index("[")]
                self.keys.add(var)

    @staticmethod
    def _is_equal_in_parentheses(line):
        if '(' in line and line.index("(") < line.index("="):
            return True
        return False


class ScanPyClass(Scan):
    def _execute(self, line, f):
        line = line.replace(' ', '')
        if line.startswith("class"):
            cls = line.strip()[5:]
            try:
                pare_start, pare_end = cls.index('('), cls.index(')')
                for func_name in cls[pare_start + 1:pare_end].split(','):
                    self.keys.add(func_name)
            except ValueError:
                pare_start, pare_end = -1, -1
            func_name = cls[:pare_start]
            self.keys.add(func_name)


class ScanImport(Scan):
    def _execute(self, line, f):
        line = line.strip().split()
        # get library name
        if line and line[0] in ("import", "from"):
            for lib in line:
                if lib.startswith(".") or lib.startswith(self.project):
                    break
                if lib not in ("import", "from"):
                    for func in lib.split("."):
                        self.special_key.add(func)
                        self.import_key.add(func)
        # get library methods
        else:
            for lib in line:
                for k in self.import_key:
                    if lib.startswith(k):
                        for func in lib.split("(")[0].split("."):
                            self.special_key.add(func)


def convert(file_dir, project, target=None):
    target_dir = file_dir.replace(project, target) if target else file_dir

    folder = f"{os.sep}".join(target_dir.split(os.sep)[:-1])
    os.makedirs(folder, exist_ok=True)
    if file_dir.endswith(".py"):
        lines = replace(file_dir)
        with open(target_dir, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    else:
        try:
            shutil.copy(file_dir, target_dir)
        except shutil.SameFileError:
            pass
    rename_file(file_dir, target_dir)


def replace(file_dir):
    with open(file_dir, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i in range(len(lines)):
        replace_string_in_pattern(i, lines)  # TODO: refactor
        replace_keys(i, lines)
        remove_single_comment(i, lines)
        remove_multi_line_comment(i, lines)
    return lines


def replace_string_in_pattern(i, lines):
    line = lines[i]

    patterns = (r'(?<=\B){.*?}(?=\B)', )
    for pattern in patterns:
        text = re.findall(pattern, lines[i])
        if text:
            for t in text:
                ori_text = t
                for k, v in mapping_table.items():
                    t = regex_replace(t, k, v)
                line = line.replace(ori_text, t)
            lines[i] = line
    patterns = (r'\w".*"', r"\w'.*'", r'".*"', r"'.*'", r"'.*\\$", r'".*\\$', r".*'", r'.*"')

    for pattern in patterns:
        text = re.findall(pattern, lines[i].strip())
        if text:
            for t in text:
                ori_text = t
                for k, v in mapping_table.items():
                    t = regex_replace(t, k, v+"@")  # template replace
                line = line.replace(ori_text, t)
            lines[i] = line
            break


def replace_keys(i, lines):
    line = lines[i]
    for k, v in mapping_table.items():
        logging.debug(f"line: {line}, K: {k}, V: {v}")
        line = regex_replace(line, k, v)
        line = line.replace(v+'@', k)  # undo template replace
    lines[i] = line


def remove_single_comment(i, lines):
    line = lines[i].strip()
    if line.startswith("#"):
        lines[i] = ''
    else:
        lines[i] = re.sub(r'#.*', '\n', lines[i])


def remove_multi_line_comment(i, lines):
    line = lines[i].strip()
    if len(line) > 3 and line.startswith('"""') and line.endswith('"""'):
        lines[i] = ''
    elif line.startswith('"""'):
        lines[i] = ''
        while not lines[i].strip().endswith('"""'):
            lines[i] = ''
            i += 1
        lines[i] = ''


def regex_replace(line, source, target):
    return re.sub(rf"\b{source}\b", target, line)


def rename_file(file_dir, target_dir):
    obfuscate_dir = target_dir.split(os.sep)
    for i, d in enumerate(obfuscate_dir):
        if d.endswith(".py"):
            d = os.path.splitext(d)[0]
        if d in mapping_table:
            obfuscate_dir[i] = mapping_table[d]
    obfuscate_dir = f'{os.sep}'.join(obfuscate_dir)
    if target_dir.endswith(".py"):
        obfuscate_dir = obfuscate_dir if obfuscate_dir.endswith(".py") else obfuscate_dir + ".py"
    folder = f"{os.sep}".join(obfuscate_dir.split(os.sep)[:-1])
    os.makedirs(folder, exist_ok=True)
    os.rename(target_dir, obfuscate_dir)
    test_path_map.update({os.path.abspath(file_dir): os.path.abspath(obfuscate_dir)})


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
