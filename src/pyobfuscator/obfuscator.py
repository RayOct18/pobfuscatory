import os
import random
import string


mapping_table = {}
unique_str = set()
test_path_map = {}


def obfuscator(project, path):
    test = True
    if path.endswith(".py"):
        file_dir = path
        scan_py(project, file_dir)
    else:
        for root, dirs, files in os.walk(path):
            for filename in files:
                file_dir = os.path.join(root, filename)
                scan_py(project, file_dir)
    if path.endswith(".py"):
        file_dir = path
        lines = convert(file_dir)
        save_file(lines, file_dir, test)
    else:
        for root, dirs, files in os.walk(path):
            for filename in files:
                file_dir = os.path.join(root, filename)
                lines = convert(file_dir)
                save_file(lines, file_dir, test)


def generate_random_string():
    return ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(3, 10)))


def update_mapping_table(func_name):
    if func_name not in mapping_table:
        random_string = generate_random_string()
        while random_string in unique_str:
            random_string = generate_random_string()
        mapping_table.update({func_name: random_string})
        unique_str.add(generate_random_string())


def save_file(lines, file_dir, test=False):
    target_dir = file_dir.replace('source', 'generated') if test else file_dir
    folder = f"{os.sep}".join(target_dir.split(os.sep)[:-1])
    os.makedirs(folder, exist_ok=True)
    with open(target_dir, 'w') as f:
        f.writelines(lines)
    obfuscate_dir = target_dir
    for k, v in mapping_table.items():
        obfuscate_dir = obfuscate_dir.replace(k, v)
    os.rename(target_dir, obfuscate_dir)
    test_path_map.update({os.path.abspath(file_dir): os.path.abspath(obfuscate_dir)})


def scan_py(project, file_dir):
    split_path = file_dir.split(os.sep)
    filename = os.path.splitext(split_path.pop())[0]
    modules = split_path[split_path.index(project)+1:]
    keys = set(modules + [filename])

    with open(file_dir, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        # functions
        if line.startswith("def"):
            func = line.replace(' ', '')[3:]
            pare_start, pare_end = func.index('('), func.index(')')
            func_name = func[:pare_start]
            keys.add(func_name)
            for func_name in func[pare_start+1:pare_end].split(','):
                keys.add(func_name)
        # variable
        elif "=" in line:
            statement = line.replace(' ', '')
            var = statement[:statement.index("=")]
            keys.add(var)

    for key in keys:
        update_mapping_table(key)


def convert(file_dir):
    with open(file_dir, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        for k, v in mapping_table.items():
            line = line.replace(k, v)
        lines[i] = line
    return lines
