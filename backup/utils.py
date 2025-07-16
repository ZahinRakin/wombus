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


try: sorted ## Introduced in 2.4
except NameError:
    def sorted(seq, cmp=None, key=None, reverse=False):
        """Copy seq and sort and return it.
        >>> sorted([3, 1, 2])
        [1, 2, 3]
        """
        seq2 = copy.copy(seq)
        if key:
            if cmp == None:
                cmp = __builtins__.cmp
            seq2.sort(lambda x,y: cmp(key(x), key(y)))
        else:
            if cmp == None:
                seq2.sort()
            else:
                seq2.sort(cmp)
        if reverse:
            seq2.reverse()
        return seq2

try:
    set, frozenset ## set builtin introduced in 2.4
except NameError:
    try:
        import sets ## sets module introduced in 2.3
        set, frozenset = sets.Set, sets.ImmutableSet
    except (NameError, ImportError):
        class BaseSet:
            "set type (see http://docs.python.org/lib/types-set.html)"


            def __init__(self, elements=[]):
                self.dict = {}
                for e in elements:
                    self.dict[e] = 1

            def __len__(self):
                return len(self.dict)

            def __iter__(self):
                for e in self.dict:
                    yield e

            def __contains__(self, element):
                return element in self.dict

            def issubset(self, other):
                for e in self.dict.keys():
                    if e not in other:
                        return False
                return True

            def issuperset(self, other):
                for e in other:
                    if e not in self:
                        return False
                return True


            def union(self, other):
                return type(self)(list(self) + list(other))

            def intersection(self, other):
                return type(self)([e for e in self.dict if e in other])

            def difference(self, other):
                return type(self)([e for e in self.dict if e not in other])

            def symmetric_difference(self, other):
                return type(self)([e for e in self.dict if e not in other] +
                                  [e for e in other if e not in self.dict])

            def copy(self):
                return type(self)(self.dict)

            def __repr__(self):
                elements = ", ".join(map(str, self.dict))
                return "%s([%s])" % (type(self).__name__, elements)

            __le__ = issubset
            __ge__ = issuperset
            __or__ = union
            __and__ = intersection
            __sub__ = difference
            __xor__ = symmetric_difference

        class frozenset(BaseSet):
            "A frozenset is a BaseSet that has a hash value and is immutable."

            def __init__(self, elements=[]):
                BaseSet.__init__(elements)
                self.hash = 0
                for e in self:
                    self.hash |= hash(e)

            def __hash__(self):
                return self.hash

        class set(BaseSet):
            "A set is a BaseSet that does not have a hash, but is mutable."

            def update(self, other):
                for e in other:
                    self.add(e)
                return self

            def intersection_update(self, other):
                for e in self.dict.keys():
                    if e not in other:
                        self.remove(e)
                return self

            def difference_update(self, other):
                for e in self.dict.keys():
                    if e in other:
                        self.remove(e)
                return self

            def symmetric_difference_update(self, other):
                to_remove1 = [e for e in self.dict if e in other]
                to_remove2 = [e for e in other if e in self.dict]
                self.difference_update(to_remove1)
                self.difference_update(to_remove2)
                return self

            def add(self, element):
                self.dict[element] = 1

            def remove(self, element):
                del self.dict[element]

            def discard(self, element):
                if element in self.dict:
                    del self.dict[element]

            def pop(self):
                key, val = self.dict.popitem()
                return key

            def clear(self):
                self.dict.clear()

            __ior__ = update
            __iand__ = intersection_update
            __isub__ = difference_update
            __ixor__ = symmetric_difference_update




#______________________________________________________________________________
# Simple Data Structures: infinity, Dict, Struct

infinity = 1.0e400

def Dict(**entries):
    """Create a dict out of the argument=value arguments.
    >>> Dict(a=1, b=2, c=3)
    {'a': 1, 'c': 3, 'b': 2}
    """
    return entries

class DefaultDict(dict):
    """Dictionary with a default value for unknown keys."""
    def __init__(self, default):
        self.default = default

    def __getitem__(self, key):
        if key in self: return self.get(key)
        return self.setdefault(key, copy.deepcopy(self.default))

    def __copy__(self):
        copy = DefaultDict(self.default)
        copy.update(self)
        return copy

class Struct:
    """Create an instance with argument=value slots.
    This is for making a lightweight object whose class doesn't matter."""
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __cmp__(self, other):
        if isinstance(other, Struct):
            return cmp(self.__dict__, other.__dict__)
        else:
            return cmp(self.__dict__, other)

    def __repr__(self):
        args = ['%s=%s' % (k, repr(v)) for (k, v) in vars(self).items()]
        return 'Struct(%s)' % ', '.join(sorted(args))

def update(x, **entries):
    """Update a dict; or an object with slots; according to entries.
    >>> update({'a': 1}, a=10, b=20)
    {'a': 10, 'b': 20}
    >>> update(Struct(a=1), a=10, b=20)
    Struct(a=10, b=20)
    """
    if isinstance(x, dict):
        x.update(entries)
    else:
        x.__dict__.update(entries)
    return x

#______________________________________________________________________________
# Functions on Sequences (mostly inspired by Common Lisp)
# NOTE: Sequence functions (count_if, find_if, every, some) take function
# argument first (like reduce, filter, and map).

def removeall(item, seq):
    """Return a copy of seq (or string) with all occurences of item removed.
    >>> removeall(3, [1, 2, 3, 3, 2, 1, 3])
    [1, 2, 2, 1]
    >>> removeall(4, [1, 2, 3])
    [1, 2, 3]
    """
    if isinstance(seq, str):
        return seq.replace(item, '')
    else:
        return [x for x in seq if x != item]

def unique(seq):
    """Remove duplicate elements from seq. Assumes hashable elements.
    >>> unique([1, 2, 3, 2, 1])
    [1, 2, 3]
    """
    return list(set(seq))

def product(numbers):
    """Return the product of the numbers.
    >>> product([1,2,3,4])
    24
    """
    return reduce(operator.mul, numbers, 1)

def count_if(predicate, seq):
    """Count the number of elements of seq for which the predicate is true.
    >>> count_if(callable, [42, None, max, min])
    2
    """
    f = lambda count, x: count + (not not predicate(x))
    return reduce(f, seq, 0)

def find_if(predicate, seq):
    """If there is an element of seq that satisfies predicate; return it.
    >>> find_if(callable, [3, min, max])
    <built-in function min>
    >>> find_if(callable, [1, 2, 3])
    """
    for x in seq:
        if predicate(x): return x
    return None

def every(predicate, seq):
    """True if every element of seq satisfies predicate.
    >>> every(callable, [min, max])
    1
    >>> every(callable, [min, 3])
    0
    """
    for x in seq:
        if not predicate(x): return False
    return True

def some(predicate, seq):
    """If some element x of seq satisfies predicate(x), return predicate(x).
    >>> some(callable, [min, 3])
    1
    >>> some(callable, [2, 3])
    0
    """
    for x in seq:
        px = predicate(x)
        if px: return px
    return False

def isin(elt, seq):
    """Like (elt in seq), but compares with is, not ==.
    >>> e = []; isin(e, [1, e, 3])
    True
    >>> isin(e, [1, [], 3])
    False
    """
    for x in seq:
        if elt is x: return True
    return False

#______________________________________________________________________________
# Functions on sequences of numbers
# NOTE: these take the sequence argument first, like min and max,
# and like standard math notation: \sigma (i = 1..n) fn(i)
# A lot of programing is finding the best value that satisfies some condition;
# so there are three versions of argmin/argmax, depending on what you want to
# do with ties: return the first one, return them all, or pick at random.

def argmin(seq, fn):
    """Return an element with lowest fn(seq[i]) score; tie goes to first one.
    >>> argmin(['one', 'to', 'three'], len)
    'to'
    """
    best = seq[0]; best_score = fn(best)
    for x in seq:
        x_score = fn(x)
        if x_score < best_score:
            best, best_score = x, x_score
    return best

def argmin_list(seq, fn):
    """Return a list of elements of seq[i] with the lowest fn(seq[i]) scores.
    >>> argmin_list(['one', 'to', 'three', 'or'], len)
    ['to', 'or']
    """
    best_score, best = fn(seq[0]), []
    for x in seq:
        x_score = fn(x)
        if x_score < best_score:
            best, best_score = [x], x_score
        elif x_score == best_score:
            best.append(x)
    return best

def argmin_random_tie(seq, fn):
    """Return an element with lowest fn(seq[i]) score; break ties at random.
    Thus, for all s,f: argmin_random_tie(s, f) in argmin_list(s, f)"""
    best_score = fn(seq[0]); n = 0
    for x in seq:
        x_score = fn(x)
        if x_score < best_score:
            best, best_score = x, x_score; n = 1
        elif x_score == best_score:
            n += 1
            if random.randrange(n) == 0:
                best = x
    return best

def argmax(seq, fn):
    """Return an element with highest fn(seq[i]) score; tie goes to first one.
    >>> argmax(['one', 'to', 'three'], len)
    'three'
    """
    return argmin(seq, lambda x: -fn(x))

def argmax_list(seq, fn):
    """Return a list of elements of seq[i] with the highest fn(seq[i]) scores.
    >>> argmax_list(['one', 'three', 'seven'], len)
    ['three', 'seven']
    """
    return argmin_list(seq, lambda x: -fn(x))

def argmax_random_tie(seq, fn):
    "Return an element with highest fn(seq[i]) score; break ties at random."
    return argmin_random_tie(seq, lambda x: -fn(x))
#______________________________________________________________________________
# Statistical and mathematical functions

def histogram(values, mode=0, bin_function=None):
    """Return a list of (value, count) pairs, summarizing the input values.
    Sorted by increasing value, or if mode=1, by decreasing count.
    If bin_function is given, map it over values first."""
    if bin_function: values = map(bin_function, values)
    bins = {}
    for val in values:
        bins[val] = bins.get(val, 0) + 1
    if mode:
        return sorted(bins.items(), key=lambda x: (x[1],x[0]), reverse=True)
    else:
        return sorted(bins.items())

def log2(x):
    """Base 2 logarithm.
    >>> log2(1024)
    10.0
    """
    return math.log10(x) / math.log10(2)

def mode(values):
    """Return the most common value in the list of values.
    >>> mode([1, 2, 3, 2])
    2
    """
    return histogram(values, mode=1)[0][0]

def median(values):
    """Return the middle value, when the values are sorted.
    If there are an odd number of elements, try to average the middle two.
    If they can't be averaged (e.g. they are strings), choose one at random.
    >>> median([10, 100, 11])
    11
    >>> median([1, 2, 3, 4])
    2.5
    """
    n = len(values)
    values = sorted(values)
    if n % 2 == 1:
        return values[n/2]
    else:
        middle2 = values[(n/2)-1:(n/2)+1]
        try:
            return mean(middle2)
        except TypeError:
            return random.choice(middle2)

def mean(values):
    """Return the arithmetic average of the values."""
    return sum(values) / float(len(values))

def stddev(values, meanval=None):
    """The standard deviation of a set of values.
    Pass in the mean if you already know it."""
    if meanval is None: meanval = mean(values)
    return math.sqrt(sum([(x - meanval)**2 for x in values]) / (len(values)-1))

def dotproduct(X, Y):
    """Return the sum of the element-wise product of vectors x and y.
    >>> dotproduct([1, 2, 3], [1000, 100, 10])
    1230
    """
    return sum([x * y for x, y in zip(X, Y)])

def vector_add(a, b):
    """Component-wise addition of two vectors.
    >>> vector_add((0, 1), (8, 9))
    (8, 10)
    """
    return tuple(map(operator.add, a, b))

def probability(p):
    "Return true with probability p."
    return p > random.uniform(0.0, 1.0)

def weighted_sample_with_replacement(seq, weights, n):
    """Pick n samples from seq at random, with replacement, with the
    probability of each element in proportion to its corresponding
    weight."""
    sample = weighted_sampler(seq, weights)
    return [sample() for s in range(n)]

def weighted_sampler(seq, weights):
    "Return a random-sample function that picks from seq weighted by weights."
    totals = []
    for w in weights:
        totals.append(w + totals[-1] if totals else w)
    return lambda: seq[bisect.bisect(totals, random.uniform(0, totals[-1]))]

def num_or_str(x):
    """The argument is a string; convert to a number if possible, or strip it.
    >>> num_or_str('42')
    42
    >>> num_or_str(' 42x ')
    '42x'
    """
    if isnumber(x): return x
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return str(x).strip()

def normalize(numbers):
    """Multiply each number by a constant such that the sum is 1.0
    >>> normalize([1,2,1])
    [0.25, 0.5, 0.25]
    """
    total = float(sum(numbers))
    return [n / total for n in numbers]

def clip(x, lowest, highest):
    """Return x clipped to the range [lowest..highest].
    >>> [clip(x, 0, 1) for x in [-1, 0.5, 10]]
    [0, 0.5, 1]
    """
    return max(lowest, min(x, highest))

#______________________________________________________________________________
## OK, the following are not as widely useful utilities as some of the other
## functions here, but they do show up wherever we have 2D grids: Wumpus and
## Vacuum worlds, TicTacToe and Checkers, and markov decision Processes.

orientations = [(1, 0), (0, 1), (-1, 0), (0, -1)]

def turn_heading(heading, inc, headings=orientations):
    return headings[(headings.index(heading) + inc) % len(headings)]

def turn_right(heading):
    return turn_heading(heading, -1)

def turn_left(heading):
    return turn_heading(heading, +1)

def distance((ax, ay), (bx, by)):
    "The distance between two (x, y) points."
    return math.hypot((ax - bx), (ay - by))

def distance2((ax, ay), (bx, by)):
    "The square of the distance between two (x, y) points."
    return (ax - bx)**2 + (ay - by)**2

def vector_clip(vector, lowest, highest):
    """Return vector, except if any element is less than the corresponding
    value of lowest or more than the corresponding value of highest, clip to
    those values.
    >>> vector_clip((-1, 10), (0, 0), (9, 9))
    (0, 9)
    """
    return type(vector)(map(clip, vector, lowest, highest))

#______________________________________________________________________________
# Misc Functions

def printf(format, *args):
    """Format args with the first argument as format string, and write.
    Return the last arg, or format itself if there are no args."""
    sys.stdout.write(str(format) % args)
    return if_(args, lambda: args[-1], lambda: format)

def caller(n=1):
    """Return the name of the calling function n levels up in the frame stack.
    >>> caller(0)
    'caller'
    >>> def f():
    ...     return caller()
    >>> f()
    'f'
    """
    import inspect
    return inspect.getouterframes(inspect.currentframe())[n][3]

