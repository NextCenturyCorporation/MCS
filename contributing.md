# Contributing to Machine Common Sense (MCS)

:+1: Thank you for considering a contribution to the MCS project.

This document is meant to guide you through our contribution process. Not only do we welcome your contributions, the MCS team would also appreciate any recommendations to the contribution process itself. 


## How Can I Contribute?

We will happily accept code, documentation improvements, issue reporting and enhancement suggestions. If you just have a question, feel free to reach out to us in the ta2-api MCS slack channel.


## Reporting Issues

If you are experiencing an issue with the MCS Python package, first check the project github issues for the existence of the same issue. If there is any new information you can add, please chime in with your details. All github (GH) issues are at https://github.com/NextCenturyCorporation/MCS/issues.

When creating a new issue, try to be as thorough as possible in describing the problem. A well-described issue will include most of the following items:
 * A detailed description of the problem/suggestion
 * Steps needed to recreate the problem
 * Version of the MCS package you are using
 * Python interpreter (Anaconda vs Python) and Python version
 * Operating System, cpu and gpu hardware


## What to expect after submitting your issue?

After providing a detailed description of your issue, someone from the MCS core team will acknowledge your new GH issue. An MCS core developer will be assigned to your issue shortly thereafter and may have clarification questions to solidify our understanding of your issue/suggestion. We will do our best to resolve your issue quickly but keep in mind that your very important issue may not be our highest priority at this particular moment. If we haven't returned to your issue in a timely manner, feel free to send a reminder for a status update.


## Closing an issue

MCS core developers will work with you until we achieve a satisfactory resolution on the issue or suggestion. In the unlikely event that your contribution or suggestion does not align with our current project direction, we may decided to close the ticket before adequate resolution. As the reporter, you may close the issue at any time.


## Pull Requests

A Pull Request (PR) for code and/or documentation should always have an associated github issue. Be sure to reference that issue in your PR. Pull requests (PR) are located at https://github.com/NextCenturyCorporation/MCS/pulls.


## Code Reviews

Since the MCS core team is accepting the responsibility of your code with the merge, we would like to ensure a reasonable level of adherence to our conventions. MCS core developers will make suggestions to help in that regard if needed. Thank you for your understanding and patience during in this stage of the process.


## Code Standards

Although there are many ways to accomplish the same thing in Python, we have developed some internal conventions to maintain standards within our own team. Adherence to this convention is the most important part of our standard. Each pull request goes through a review process by an MCS core developer to ensure adherence to these standards.


### Docstrings

Most functions, methods, classes, modules need an associated docstring. Docstrings help describe our [API DOCS](machine_common_sense/API.md). This documentation is automatically created from source code during each code commit thanks to our use of [Sphinx](machine_common_sense/DEV.md#Sphinx).

```python
def add(x: int, y: int) -> int:
  '''Adds two integers.

  Args:
    x (int): The first addend
    y (int): The second addend

  Returns:
    The sum of the two addends.
  '''
```

[PEP-257](https://www.python.org/dev/peps/pep-0257/)


### Type Hints

We prefer type hints to additionally help with API explanability. Although python is a loosely-type language, type hinting helps core developers and contributors better understand the inputs and return types of our API.

```python
def add(x: int, y: int) -> int:
  return x + y
```

[PEP-484](https://www.python.org/dev/peps/pep-0484/)


### Linting

See the [DEV Reference](machine_common_sense/DEV.md#Linting) for more on our linting approach and necessary setup steps.

[PEP-8](https://www.python.org/dev/peps/pep-0008/)


### Imports

Internal MCS modules use relative imports as in:

```python
from .goal_metadata import GoalMetadata
```

As a general rule, we never use `import *` as it pollutes the namespace.

> "Explicit is better than implicit" - Tim Peters, The Zen of Python


### Unit Tests

All MCS unit tests are run from the MCS project root using:

```bash
$ python -m unittest
```

Our Jenkins continuous integration server also runs unit tests in this way.

You can run a specific module's test during development using:

```bash
$ python -m unittest tests.test_module
```

For us, unit tests serve a dual purpose of code maintainability as well as providing a form of documentation for contributors. We encourage namespace usage of the MCS package and unit test should reflect this notion unless the module is intended for internal use only. See [`test_plotter.py`](tests/test_plotter.py) for an example of internal module unit testing.

```python
import unittest
import machine_common_sense as mcs

class TestClass(unittest.TestCase):
  def test_rotation_key(self):
    controller = mcs.controller()
    self.assertEquals(controller.ROTATION_KEY, 'rotation')
```

For more information on unit testing, see our [testing documentation](https://github.com/NextCenturyCorporation/MCS/blob/development/tests/README.md)


#### Test Resource Pathing

In some instances, referencing a local test resource file is needed. Since unit tests are run from the root folder, paths to resources should include the 'tests' folder prefix.

```python
with open('tests/test.msgpack', 'rb') as file
```

### Adding Package Dependencies

If your contribution is adding a dependency to the MCS package, you'll need to add that dependency to the requirements.txt file with a pinned version. The purpose of the pinned version is to ensure all developers are working in the same environment.

```
# requirements.txt
new_pkg==1.2.3
```

The new dependency will also have to be added to `setup.py` in `install_requires`. The dependency version here needs to be more lenient so as not to conflict with other installed packages. This may require additional testing with different versions of the new package to ensure functional consistency.

```python
# setup.py
setuptools.setup(
    name='machine_common_sense',
    install_requires=[
      'matplotlib>=3.3',
      'msgpack>=1.0.0'
    ]
)
```


### Adding New MCS Modules

```python
from .new_module import ModuleClass
```

if exposed to mcs, add to `__init__.py` so that it is readily available from the mcs namespace. If your module is only used internally, there's no need to add to `__init__.py`. Encourage namespaced use of the package. Usage becomes:

```python
import machine_common_sense as mcs

mod_cls = mcs.ModuleClass()
```

This is to avoid the pattern of importing and not having class/function namespaced.

```python
from machine_common_sense.new_module import ModuleClass
mod_cls = ModuleClass()
```

> Namespaces are one honking great idea—let's do more of those! - Tim Peters, The Zen of Python
