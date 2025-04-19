#!/usr/bin/env python3
"""
tests for the MS wrapper
"""

from MeasureSuiteCommandLine import MS


def test_simple():
    """
    test only object file
    """
    files = ["test/test.o", "test/test2.o"]
    w = MS(files=files)
    assert not w.error()
    b, d = w.run()
    assert b
    print(d)

    assert d.stats.numFunctions == 2
    assert d.stats.incorrect == 0
    assert d.stats.timer == "PMC"
    assert len(d.functions) == 2
    assert len(d.avgs) == 2
    assert len(d.medians) == 2
    assert len(d.cycles) == 2
    assert len(d.cycles[0]) == 31
    assert len(d.cycles[1]) == 31


def test_compile():
    """
    test the compiler
    """
    files = ["test/c/test.c", "test/c/test2.c"]
    w = MS(files)
    assert not w.error()
    b, d = w.run()
    assert b

    assert d.stats.numFunctions == 2
    assert d.stats.incorrect == 0
    assert d.stats.timer == "PMC"
    assert len(d.functions) == 2
    assert len(d.avgs) == 2
    assert len(d.medians) == 2
    assert len(d.cycles) == 2
    assert len(d.cycles[0]) == 31
    assert len(d.cycles[1]) == 31


def test_assembly():
    """
    test the assembler 
    """
    files = ["test/asm/test.asm", "test/asm/test2.asm"]
    w = MS(files)
    assert not w.error()
    b, d = w.run()
    assert b

    assert d.stats.numFunctions == 2
    assert d.stats.incorrect == 0
    assert d.stats.timer == "PMC"
    assert len(d.functions) == 2
    assert len(d.avgs) == 2
    assert len(d.medians) == 2
    assert len(d.cycles) == 2
    assert len(d.cycles[0]) == 31
    assert len(d.cycles[1]) == 31


def test_assembly_str():
    """
    test the
    """
    data = """mov rax, [rsi]
add rax, [rdx]
mov [rdi], rax
ret"""

    files = [data]
    w = MS(files)
    assert not w.error()
    b, d = w.run()
    assert b

    assert d.stats.numFunctions == 1
    assert d.stats.incorrect == 0
    assert d.stats.timer == "PMC"
    assert len(d.functions) == 1
    assert len(d.avgs) == 1
    assert len(d.medians) == 1
    assert len(d.cycles) == 1
    assert len(d.cycles[0]) == 31


if __name__ == '__main__':
    # test_simple()
    # test_compile()
    # test_assembly()
    test_assembly_str()
