from MeasureSuiteCommandLine import MSC


def test_simple():
    """
    test
    """
    files = ["test/asm/add_two_numbers.asm", "test/asm/add_two_numbers2.asm"]
    w = MSC(files)
    status, d = w.run()
    assert status

    print(d)

