from MeasureSuiteCommandLine import Msc


def test_version():
    """simply checks if the __version__ function existsA
    """
    w = Msc([]).__version__()
    assert w

def test_simple():
    """
    test the simplest version
    """
    files = ["test/add_two_numbers.asm", "test/add_two_numbers2.asm"]
    w = Msc(files)
    data = w.execute()
    assert(data)
