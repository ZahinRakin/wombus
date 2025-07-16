"""Representations and Inference for Logic (Chapters 7-9, 12)

Covers both Propositional and First-Order Logic. First we have four
important data types:

    KB            Abstract class holds a knowledge base of logical expressions
    Expr          A logical expression
    substitution  Implemented as a dictionary of var:value pairs, {x:1, y:x}

Be careful: some functions take an Expr as argument, and some take a KB.
Then we implement various functions for doing logical inference:

    tt_entails       Say if a statement is entailed by a KB

And a few other functions:

    to_cnf           Convert to conjunctive normal form

[ebreck]: This module has been simplified to the subset of code needed for
Assignment 3.
"""

import collections
import itertools, re
from utils import *

#______________________________________________________________________________

class KB:
    """A knowledge base to which you can tell and ask sentences.
    To create a KB, first subclass this class and implement
    tell, ask_generator, and retract.  Why ask_generator instead of ask?
    The book is a bit vague on what ask means --
    For a Propositional Logic KB, ask(P & Q) returns True or False, but for an
    FOL KB, something like ask(Brother(x, y)) might return many substitutions
    such as {x: Cain, y: Abel}, {x: Abel, y: Cain}, {x: George, y: Jeb}, etc.
    So ask_generator generates these one at a time, and ask either returns the
    first one or returns False."""

    def __init__(self, sentence=None):
        abstract

    def tell(self, sentence):
        "Add the sentence to the KB."
        abstract

    def ask(self, query):
        """Return a substitution that makes the query true, or,
        failing that, return False."""
        for result in self.ask_generator(query):
            return result
        return False

    def ask_generator(self, query):
        "Yield all the substitutions that make query true."
        abstract

    def retract(self, sentence):
        "Remove sentence from the KB."
        abstract


