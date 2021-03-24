# MCS Python Library: Testing README

Unit tests for the Machine Common Sense (MCS) project are written using the unittest framework.

https://docs.python.org/3.6/library/unittest.html

## Running All Tests

From the MCS project root folder, run the unittest module. This is how our CI/CD pipeline will run tests.

```bash
(venv) $ python -m unittest
```

### Testing a Specific Module

To run a specific test module, provide the `tests` folder along with the module name as the unittest argument.

```bash
(venv) $ python -m unittest tests.test_module
```

Alternatively, if the test module includes a `__main__`, the tester should be able to run:

```bash
(venv) $ python tests/test_module.py
```

### Running a Specific Test

To run a specific test, add the test class and method name to the unittest argument.

```bash
(venv) $ python -m unittest test.test_module.TestClass.test_method
```

## Writing Tests

1. All unit tests and associated test resources for the MCS project will reside in the `tests` folder.
2. Pathing for test resources should keep in mind that tests will be run using our CI/CD pipeline from the MCS root folder.
3. The name of your test file should be the module under test but prepended with `test_`. For example, if we were writting tests for `foo.py`, the corresponding test module within the tests folder would be `test_foo.py`.
4. The test class should extend `unittest.TestCase` and begin with `Test`as in `class TestFoo(unittest.TestCase`.
5. The name of each test method should start with `test_` and accept `self` as an argument. 
6. Use  `self.assert*` functions to make your test assertions.
7. Add `setUpClass(class)` and/or `tearDownClass(class)` as needed to custom custom behavior before or after each test module is run.
8. Add `setUp(self)` and/or `tearDown(self)`functions as needed to run custom behavior before or after each individual unit test.
9. As a general rule, unit tests should clean up after themselves. If the test creates something, it should also destroy it so that the project state returns to normal.
10. Unit tests should check for both expected and unexpected cases. For example, what happens when the input is `None`? If your function throws an exception, test that condition as well.
11. Reference existing test modules for examples as necessary.
