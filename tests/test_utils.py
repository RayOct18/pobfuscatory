from pyobfuscator.obfuscator import collect_library_keyword


def test_collect_keyword():
    seen = collect_library_keyword()
    assert len(seen) != 0


def test_collect_keyword_not_exists():
    seen = collect_library_keyword(["test"])
    assert len(seen) != 0
