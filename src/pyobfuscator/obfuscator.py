import os
import re
import random
import string


mapping_table = {"source": "generated"}
unique_str = set()
test_path_map = {}
special_key = ("__init__", "self", "", "'", '"')


def generate_random_string():
    return ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(3, 10)))


class Obfuscator:
    def __init__(self, project, path, target=None):
        self.project = project
        self.path = path
        self.target = target

    def obfuscate(self):
        self._scan()
        self._convert()
        if self.target:
            self.path = self.path.replace(self.project, self.target)
        clean_empty_folder(self.path)

    def _process_file(self, func, **kwargs):
        if self.path.endswith(".py"):
            file_dir = self.path
            func(file_dir, **kwargs)
        else:
            for root, dirs, files in os.walk(self.path):
                for filename in files:
                    file_dir = os.path.join(root, filename)
                    if kwargs.get("target"):
                        func(file_dir, kwargs["project"], kwargs["target"])
                    else:
                        if filename != '__init__.py':
                            func(file_dir)

    def _scan(self):
        self._process_file(Scan(self.project).run)

    def _convert(self):
        self._process_file(convert, project=self.project, target=self.target)


class Scan:
    keys = set()

    def __init__(self, project):
        self.project = project

    def _scan_external(self, file_dir):
        split_path = file_dir.split(os.sep)
        filename = os.path.splitext(split_path.pop())[0]
        modules = split_path[split_path.index(self.project) + 1:]
        for module in modules + [filename]:
            self.keys.add(module)

    def run(self, file_dir):
        self._scan_external(file_dir)

        with open(file_dir, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.replace(' ', '')
            for subclass in Scan.__subclasses__():
                subclass(self.project)._execute(line)

        self._update_mapping_table()

    def _execute(self, line):
        raise NotImplementedError

    def _update_mapping_table(self):
        for func_name in self.keys:
            if func_name not in mapping_table and func_name not in special_key:
                random_string = generate_random_string()
                while random_string in unique_str:
                    random_string = generate_random_string()
                mapping_table.update({func_name: random_string})
                unique_str.add(generate_random_string())


class ScanPyFunc(Scan):
    def _execute(self, line):
        if line.startswith("def"):
            func = line[3:]
            pare_start, pare_end = func.index('('), func.index(')')
            func_name = func[:pare_start]
            self.keys.add(func_name)
            for func_name in func[pare_start+1:pare_end].split(','):
                self.keys.add(func_name)


class ScanPyVar(Scan):
    def _execute(self, line):
        if "=" in line and not line.startswith("def"):
            var = line[:line.index("=")]
            self.keys.add(var)


class ScanPyClass(Scan):
    def _execute(self, line):
        if line.startswith("class"):
            cls = line[5:]
            try:
                pare_start, pare_end = cls.index('('), cls.index(')')
                for func_name in cls[pare_start + 1:pare_end].split(','):
                    self.keys.add(func_name)
            except ValueError:
                pare_start, pare_end = -1, -1
            func_name = cls[:pare_start]
            self.keys.add(func_name)


def convert(file_dir, project, target=None):
    lines = replace(file_dir)
    save_file(lines, file_dir, project, target)


def replace(file_dir):
    with open(file_dir, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        replace_keys(i, lines)
        remove_single_comment(i, lines)
        remove_multi_line_comment(i, lines)
    return lines


def replace_keys(i, lines):
    line = lines[i]
    for k, v in mapping_table.items():
        line = regex_replace(line, k, v)
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


def save_file(lines, file_dir, project, target=None):
    target_dir = file_dir.replace(project, target) if target else file_dir
    folder = f"{os.sep}".join(target_dir.split(os.sep)[:-1])
    os.makedirs(folder, exist_ok=True)
    with open(target_dir, 'w') as f:
        f.writelines(lines)
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
