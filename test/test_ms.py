from MeasureSuiteCommandLine import Wrapper_MS


def test_simple():
    """
    test the 
    """
    files = ["test/test.o", "test/test2.o"]
    w = Wrapper_MS(files) 
    w.run()
