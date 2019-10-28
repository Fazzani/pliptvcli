import inspect
import os
import re
import sys
from functools import lru_cache
from typing import List, Any, Tuple


@lru_cache(maxsize=32)
def load_modules_from_path(path, pattern: str = r".+\ d.py$") -> List[Tuple[str, str]]:
    """
   Import all modules from the given directory
   """
    # Check and fix the path
    if path[-1:] != "/":
        path += "/"

    # Get a list of files in the directory, if the directory exists
    if not os.path.exists(path):
        raise OSError("Directory does not exist: %s" % path)

    # Add path to the system path
    sys.path.append(path)
    list_mod: List[Tuple[str, str]] = []
    # Load all the files in path
    for f in os.listdir(path):
        # Ignore anything that isn't a .py file
        if len(f) > 3 and f[-3:] == ".py" and re.match(pattern, f, re.I):
            modname = f[:-3]
            list_mod += [(modname, os.path.join(path, f))]
            # Import the module
            __import__(modname, globals(), locals(), ["*"])
    return list_mod


def load_class_from_name(fqcn: str) -> Any:
    """Build class instance from class name

    Arguments:
        fqcn {[type]} -- full class name

    Raises:
        TypeError: [description]

    Returns:
        Any -- return class instance
    """
    # Break apart fqcn to get module and class name
    paths = fqcn.split(".")
    module_name = ".".join(paths[:-1])
    class_name = paths[-1]
    # Import the module
    __import__(module_name, globals(), locals(), ["*"])
    # Get the class
    cls = getattr(sys.modules[module_name], class_name)
    # Check cls
    if not inspect.isclass(cls):
        raise TypeError("%s is not a class" % fqcn)
    # Return class
    return cls


def class_list_from_modules(module: str, predicate=None) -> List[str]:
    return [
        name
        for name, obj in inspect.getmembers(sys.modules[module], predicate)
        if inspect.isclass(obj)
    ]
