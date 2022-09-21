from pyobfuscator.obfuscator import insert_confuse_line


def test_insert_confuse_line():
    lines = ["\n", "def hello_world():\n", "    print('hello world')", "\n"]
    expected = [0, 0, 4, 0]
    for i in range(len(lines)):
        res = insert_confuse_line(i, lines, [], 1)
        assert len(res[0]) - len(res[0].lstrip()) == expected[i]
