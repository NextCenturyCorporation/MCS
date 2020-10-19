# MCS Python Library: Testing README

## Running Tests

```
python -m unittest
```

## Writing Tests

https://docs.python.org/3.6/library/unittest.html

1. The name of your test file should start with `test`.
2. The name of your test class inside your test file should match the name of your test file (case insensitive).
3. Import `unittest`. Your test class should extend `unittest.TestCase`.
4. The name of each test function should start with `test` and accept `self` as an argument. Use the `self.assert*` functions to make your test assertions.
5. Add `setUp(self)` and/or `tearDown(self)` functions to run custom behavior before or after each individual unit test.

