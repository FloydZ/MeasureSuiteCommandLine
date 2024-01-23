from MeasureSuiteCommandLine import Wrapper_MS


def test_simple():
    """
    test only object file
    """
    files = ["test/test.o", "test/test2.o"]
    w = Wrapper_MS(files)
    print(w.run())


def test_compile():
    """
    test that only i
    """
    files = ["test/test.c", "test/test2.c"]
    w = Wrapper_MS(files)
    print(w.run())


def test_assembly():
    """
    test the 
    """
    files = ["test/test.asm", "test/test2.asm"]
    w = Wrapper_MS(files)
    print(w.run())
