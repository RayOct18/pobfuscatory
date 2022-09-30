# PObfuscatory
python code obfuscator, you can obfuscate a file or an entire project.

# Install
```bash
pip install git+https://github.com/RayOct18/pobfuscatory
```

# Usage
**Note:**
If your project use not built-in library, you need to install it first.
The obfuscator needs to scan all modules and functions from third-party libraries to exclude the keywords.

```bash
# single file
$ python -m pobfuscatory -s ./single_file/raw/hello_world.py -t ./obfuscated

# whole project
$ python -m pobfuscatory -s ./src/pobfuscatory -t ./examples/project/obfuscated

# preserve some key (obfuscator, Keys)
$ python -m pobfuscatory -s ./src/pobfuscatory -t ./examples/project/obfuscated -e obfuscator Keys

# adjust confuse line insertion, probability (0.0~1.0), repeat number(1~)
$ python -m pobfuscatory -s ./src/pobfuscatory -t ./examples/project/obfuscated -p 0.5 -r 5
# close confuse line
$ python -m pobfuscatory -s ./src/pobfuscatory -t ./examples/project/obfuscated -p 0

# open debug log
$ python -m pobfuscatory -s ./src/pobfuscatory -t ./examples/project/obfuscated -v 1
```

# Examples
**Single file:**
[ [raw](https://github.com/RayOct18/pobfuscatory/blob/main/examples/single_file/raw/hello_world.py) ]
[ [obfuscated](https://github.com/RayOct18/pobfuscatory/blob/main/examples/single_file/obfuscated/VGWPPEYHANJ.py) ]

**Whole project:**
[ [raw](https://github.com/RayOct18/pobfuscatory/tree/main/src/pobfuscatory) ]
[ [obfuscated](https://github.com/RayOct18/pobfuscatory/tree/main/examples/project/obfuscated) ]
