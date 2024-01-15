from MeasureSuiteCommandLine import Wrapper_MSC


def test_simple():
    """
    test the 
    """
    files = ["test/add_two_numbers.asm", "test/add_two_numbers2.asm"]
    w = Wrapper_MSC(files) 
