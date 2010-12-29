#!/usr/bin/env python
# -*- coding: utf-8 -*-
# patterns.py: Common wildcard searching/filtering functionality for files.
#
# Copyright (C) 2010 Gora Khargosh <gora.khargosh@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from fnmatch import fnmatch, fnmatchcase
import string

__all__ = ['match', 'match_against', 'filter']

def match_against(pathname, patterns, case_sensitive=True):
    """
    Determines whether the pathname matches any of the given wildcard patterns,
    optionally ignoring the case of the pathname and patterns.

    :param pathname:
        A path name that will be matched against a wildcard pattern.
    :param patterns:
        A list of wildcard patterns to match the filename against.
    :param case_sensitive:
        ``True`` if the matching should be case-sensitive; ``False`` otherwise.
    :returns:
        ``True`` if the pattern matches; ``False`` otherwise.

    Usage:
    >>> match_against("/home/username/foobar/blah.py", ["*.py", "*.txt"], False)
    True
    >>> match_against("/home/username/foobar/blah.py", ["*.PY", "*.txt"], True)
    False
    >>> match_against("/home/username/foobar/blah.py", ["*.PY", "*.txt"], False)
    True
    >>> match_against("C:\\windows\\blah\\BLAH.PY", ["*.py", "*.txt"], True)
    False
    >>> match_against("C:\\windows\\blah\\BLAH.PY", ["*.py", "*.txt"], False)
    True
    """
    if case_sensitive:
        match_func = fnmatchcase
        pattern_transform_func = (lambda w: w)
    else:
        match_func = fnmatch
        pathname = pathname.lower()
        pattern_transform_func = (lambda w: w.lower())
    for pattern in set(patterns):
        pattern = pattern_transform_func(pattern)
        if match_func(pathname, pattern):
            return True
    return False


def _match(pathname,
           included_patterns,
           excluded_patterns,
           case_sensitive=True):
    """Internal function same as :func:`match` but does not check arguments.

    Usage:
    >>> _match("/users/gorakhargosh/foobar.py", ["*.py"], ["*.PY"], True)
    True
    >>> _match("/users/gorakhargosh/FOOBAR.PY", ["*.py"], ["*.PY"], True)
    False
    >>> try: _match("/users/gorakhargosh/FOOBAR.PY", ["*.py"], ["*.PY"], False)
    >>> except ValueError: pass
    >>> _match("/users/gorakhargosh/foobar/", ["*.py"], ["*.txt"], False)
    False
    """
    if not case_sensitive:
        included_patterns = set(map(string.lower, included_patterns))
        excluded_patterns = set(map(string.lower, excluded_patterns))
    else:
        included_patterns = set(included_patterns)
        excluded_patterns = set(excluded_patterns)
    common_patterns = included_patterns & excluded_patterns
    if common_patterns:
        raise ValueError('patterns `%s` specified to be included and excluded' % common_patterns)
    return \
        match_against(pathname, included_patterns, case_sensitive) \
        and not match_against(pathname, excluded_patterns, case_sensitive)


def match(pathname,
          included_patterns=None,
          excluded_patterns=None,
          case_sensitive=True):
    """
    Matches a pathname against a set of acceptable and ignored patterns.

    :param pathname:
        A pathname which will be matched against a pattern.
    :param included_patterns:
        Allow filenames matching wildcard patterns specified in this list.
    :param excluded_patterns:
        Ignores filenames matching wildcard patterns specified in this list.
    :param case_sensitive:
        ``True`` if matching should be case-sensitive; ``False`` otherwise.
    :returns:
        ``True`` if the pathname matches; ``False`` otherwise.
    """
    included = ["*"] if included_patterns is None else included_patterns
    excluded = [] if excluded_patterns is None else excluded_patterns
    return _match(pathname, included, excluded, case_sensitive)


def filter(pathnames,
           included_patterns=None,
           excluded_patterns=None,
           case_sensitive=True):
    """
    Filters from a set of paths based on acceptable patterns and
    ignorable patterns.

    :param pathnames:
        A list of path names that will be filtered based on matching and
        ignored patterns.
    :param included_patterns:
        Allow filenames matching wildcard patterns specified in this list.
    :param excluded_patterns:
        Ignores filenames matching wildcard patterns specified in this list.
    :param case_sensitive:
        ``True`` if matching should be case-sensitive; ``False`` otherwise.
    :returns:
        A list of pathnames that matched the allowable patterns and passed
        through the ignored patterns.
    """
    included = ["*"] if included_patterns is None else included_patterns
    excluded = [] if excluded_patterns is None else excluded_patterns

    for pathname in pathnames:
        # We don't call the public match because it checks arguments
        # and sets default values if none are found. We're already doing that
        # above.
        if _match(pathname, included, excluded, case_sensitive):
            yield pathname


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
