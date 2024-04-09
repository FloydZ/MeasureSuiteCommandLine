from MeasureSuiteCommandLine import MS



def test_simple():
    """
    test only object file
    """
    files = ["test/test.o", "test/test2.o"]
    w = MS(files)
    assert not w.error()
    d = w.run()

    assert d.stats.numFunctions == 2
    assert d.stats.runtime == 0
    assert d.stats.incorrect == 0
    assert d.stats.timer == "PMC"
    assert len(d.functions) == 2
    assert len(d.avgs) == 2
    assert len(d.medians) == 2
    assert len(d.cycles) == 2
    assert len(d.cycles[0]) == 31
    assert len(d.cycles[1]) == 31
f


def test_compile():
    """
    test the compiler
    """
    files = ["test/c/test.c", "test/c/test2.c"]
    w = MS(files)
    assert not w.error()
    d = w.run()
    assert d.stats.numFunctions == 2
    assert d.stats.runtime == 0
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
    d = w.run()
    assert d.stats.numFunctions == 2
    assert d.stats.runtime == 0
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
    d = w.run()
    assert d.stats.numFunctions == 2
    assert d.stats.runtime == 0
    assert d.stats.incorrect == 0
    assert d.stats.timer == "PMC"
    assert len(d.functions) == 2
    assert len(d.avgs) == 2
    assert len(d.medians) == 2
    assert len(d.cycles) == 2
    assert len(d.cycles[0]) == 31
    assert len(d.cycles[1]) == 31
