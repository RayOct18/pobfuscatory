from pyobfuscator.obfuscator import (
    generate_confuse_line,
    insert_confuse_line,
    get_last_bracket_index,
)


def test_generate_confuse_line():
    lines = ["\n", "def hello_world():\n", "    print('hello world')", "\n"]
    cache = []
    stack = []
    for i in range(len(lines)):
        _ = generate_confuse_line(i, lines, cache, stack, 1)
    assert len(cache[0][1]) - len(cache[0][1].lstrip()) == 4
    assert len(cache) == 1


def test_generate_confuse_line_def():
    lines = [
        "\n",
        "def hello_world(\n",
        "x,\n",
        "    ):\n",
        "    print('hello world')",
        "\n",
    ]
    i = 0
    cache = []
    stack = []
    while i < len(lines):
        i = generate_confuse_line(i, lines, cache, stack, 1)
        i += 1
    assert len(cache) == 1


def test_generate_confuse_line_brackets():
    lines = ["\n", "x = {\n", "'x': 1\n", "}\n", "y = 3\n", "\n"]
    i = 0
    cache = []
    stack = []
    while i < len(lines):
        i = generate_confuse_line(i, lines, cache, stack, 1)
        i += 1
    assert len(cache) == 1


def test_generate_confuse_line_if_else():
    lines = [
        "\n",
        "if x > y:\n",
        "    x = 1\n",
        "else:\n",
        "    print('hello world')",
        "\n",
    ]
    i = 0
    cache = []
    stack = []
    while i < len(lines):
        i = generate_confuse_line(i, lines, cache, stack, 1)
        i += 1
    assert len(cache) == 3


def test_generate_confuse_line_try_except():
    lines = [
        "\n",
        "try:\n",
        "    x = 1\n",
        "except:\n",
        "    print('hello world')",
        "\n",
    ]
    i = 0
    cache = []
    stack = []
    while i < len(lines):
        i = generate_confuse_line(i, lines, cache, stack, 1)
        i += 1
    assert len(cache) == 3


def test_insert_confuse_line():
    lines = ["\n", "def hello_world():\n", "    print('hello world')", "\n"]
    cache = []
    stack = []
    for i in range(len(lines)):
        _ = generate_confuse_line(i, lines, cache, stack, 1)
    res = insert_confuse_line(lines, cache)
    assert len(res) == 5


def test_get_last_brackets1():
    lines = ["x = print(\n", "x(1), y(2), \n", ")\n", "z = 3\n", "\n"]
    stack = []
    i = 0
    i = get_last_bracket_index(i, lines, stack, r"\(|\)", "(")
    assert i == 2


def test_get_last_brackets2():
    lines = ["x = print(x(1), y(2))\n", "z = 3\n", "\n"]
    stack = []
    i = 0
    while i < len(lines):
        i = get_last_bracket_index(i, lines, stack, r"\(|\)", "(")
        if not stack:
            break
        i += 1
    assert i == 0


def test_get_last_brackets3():
    lines = ["x = [\n", "x(1), y(2), \n", "]\n", "z = 3\n", "\n"]
    stack = []
    i = 0
    i = get_last_bracket_index(i, lines, stack, r"\[|\]", "[")
    assert i == 2
