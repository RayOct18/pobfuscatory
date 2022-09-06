import os
import re
from os import listdir


def concat_path(path, file):
    return os.path.join(path, file)


def from_import(file_dir):
    return listdir(file_dir)


def name_conflict(listdir):
    return listdir + 1


def assign_library(x):
    exists = False
    o = os
    return o.path.exists(x)
