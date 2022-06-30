import os
import re
import random
import string


mapping_table = {"source": "generated"}
unique_str = set()
test_path_map = {}


def generate_random_string():
    return ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(3, 10)))


class Obfuscator:
    def __init__(self, project, path, test=False):
        self.project = project
        self.path = path
        self.test = test

    def obfuscate(self):
        self._scan()
        self._convert()
        if self.test:
            self.path = self.path.replace("source", "generated")
        clean_empty_folder(self.path)

    def _process_file(self, func, **kwargs):
        if self.path.endswith(".py"):
            file_dir = self.path
            func(file_dir, *kwargs)
        else:
            for root, dirs, files in os.walk(self.path):
                for filename in files:
                    file_dir = os.path.join(root, filename)
                    if kwargs.get("test"):
                        func(file_dir, kwargs["test"])
                    else:
                        if filename != '__init__.py':
                            func(file_dir)

    def _scan(self):
        self._process_file(Scan(self.project).run)

    def _convert(self):
        self._process_file(convert, test=self.test)


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
            for subclass in Scan.__subclasses__():
                subclass(self.project)._execute(line)

            self._update_mapping_table()

    def _execute(self, line):
        raise NotImplementedError

    def _update_mapping_table(self):
        for func_name in self.keys:
            if func_name not in mapping_table:
                random_string = generate_random_string()
                while random_string in unique_str:
                    random_string = generate_random_string()
                mapping_table.update({func_name: random_string})
                unique_str.add(generate_random_string())


class ScanPyFunc(Scan):
    def _execute(self, line):
        if line.startswith("def"):
            func = line.replace(' ', '')[3:]
            pare_start, pare_end = func.index('('), func.index(')')
            func_name = func[:pare_start]
            self.keys.add(func_name)
            for func_name in func[pare_start+1:pare_end].split(','):
                self.keys.add(func_name)


class ScanPyVar(Scan):
    def _execute(self, line):
        if "=" in line and not line.startswith("def"):
            statement = line.replace(' ', '')
            var = statement[:statement.index("=")]
            self.keys.add(var)


def convert(file_dir, test=False):
    lines = replace(file_dir)
    save_file(lines, file_dir, test)


def replace(file_dir):
    with open(file_dir, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        for k, v in mapping_table.items():
            line = regex_replace(line, k, v)
        lines[i] = line
    return lines


def regex_replace(line, source, target):
    return re.sub(rf"\b{source}\b", target, line)


def save_file(lines, file_dir, test=False):
    target_dir = file_dir.replace('source', 'generated') if test else file_dir
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
    obfuscate_dir = f'{os.sep}'.join(obfuscate_dir) + ".py"
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
