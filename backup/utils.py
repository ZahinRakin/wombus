"""Provide some widely useful utilities. Safe for "from utils import *".

"""

from __future__ import generators
import operator, math, random, copy, sys, os.path, bisect, re

assert (2,5) <= sys.version_info < (3,), """\
This code is meant for Python 2.5 through 2.7.
You might find that the parts you care about still work in older
Pythons or happen to work in newer ones, but you're on your own --
edit utils.py if you want to try it."""

#______________________________________________________________________________
# Compatibility with Python 2.2, 2.3, and 2.4

# The AIMA code was originally designed to run in Python 2.2 and up.
# The first part of this file implements for Python 2.2 through 2.4
# the parts of 2.5 that the original code relied on. Now we're
# starting to go beyond what can be filled in this way, but here's
# the compatibility code still since it doesn't hurt:

try: bool, True, False ## Introduced in 2.3
except NameError:
    class bool(int):
        "Simple implementation of Booleans, as in PEP 285"
        def __init__(self, val): self.val = val
        def __int__(self): return self.val
        def __repr__(self): return ('False', 'True')[self.val]

    True, False = bool(1), bool(0)

try: sum ## Introduced in 2.3
except NameError:
    def sum(seq, start=0):
        """Sum the elements of seq.
        >>> sum([1, 2, 3])
        6
        """
        return reduce(operator.add, seq, start)

try: enumerate  ## Introduced in 2.3
except NameError:
    def enumerate(collection):
        """Return an iterator that enumerates pairs of (i, c[i]). PEP 279.
        >>> list(enumerate('abc'))
        [(0, 'a'), (1, 'b'), (2, 'c')]
        """
        ## Copied from PEP 279
        i = 0
        it = iter(collection)
        while 1:
            yield (i, it.next())
            i += 1


try: reversed ## Introduced in 2.4
except NameError:
    def reversed(seq):
        """Iterate over x in reverse order.
        >>> list(reversed([1,2,3]))
        [3, 2, 1]
        """
        if hasattr(seq, 'keys'):
            raise TypeError("mappings do not support reverse iteration")
        i = len(seq)
        while i > 0:
            i -= 1
            yield seq[i]


