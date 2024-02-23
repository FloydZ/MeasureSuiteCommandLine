from MeasureSuiteCommandLine import Ms


def test_simple():
    """
    test only object file
    """
    files = ["test/test.o", "test/test2.o"]
    w = Ms(files).run()
    print(w)


def test_compile():
    """
    test the compiler
    """
    files = ["test/test.c", "test/test2.c"]
    w = Ms(files).run()
    print(w)


def test_assembly():
    """
    test the assembler 
    """
    files = ["test/test.asm", "test/test2.asm"]
    w = Ms(files).run()
    assert w
    print(w)
