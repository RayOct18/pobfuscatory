import os


def obfuscator(project, path):
    if path.endswith(".py"):
        file_dir = path
        convert(project, file_dir)
    else:
        for root, dirs, files in os.walk(path):
            for filename in files:
                file_dir = os.path.join(root, filename)
    return


def convert(project, file_dir):
    split_path = file_dir.split(os.sep)
    filename = split_path.pop()
    modules = split_path[split_path.index(project):]
    print(filename, modules)