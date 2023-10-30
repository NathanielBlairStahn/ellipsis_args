import pytest
from ellipsis_args.functional import partially_applicable

@partially_applicable
def f(a, b, c, d=1, e=2):
    return f'{a=}, {b=}, {c=}, {d=}, {e=}'

@partially_applicable
def f_no_kwargs(a, b, c):
    return f'{a=}, {b=}, {c=}'

@partially_applicable
def g(*args, **kwargs):
    return args, kwargs

def test_f_no_kwargs():
    assert f_no_kwargs(3, 5, 7) == 'a=3, b=5, c=7'
    assert f_no_kwargs(..., 5, 7)(3) == 'a=3, b=5, c=7'
    assert f_no_kwargs(3, ..., 7)(5) == 'a=3, b=5, c=7'
    assert f_no_kwargs(3, ..., ...)(5, 7) == 'a=3, b=5, c=7'
    assert f_no_kwargs(..., 5, ...)(3, 7) == 'a=3, b=5, c=7'
    assert f_no_kwargs(..., ..., c=7)(3, 5) == 'a=3, b=5, c=7'
    assert f_no_kwargs(..., b=5, c=7)(3) == 'a=3, b=5, c=7'
    # Raises SyntaxError: positional argument follows keyword argument
    # since ... comes after b=5. This happens on compilation, so can't run:
    # assert f_no_kwargs(..., b=5, ...)(3, 7) == 'a=3, b=5, c=7'
    assert f_no_kwargs(..., b=5, c=...)(3, c=7) == 'a=3, b=5, c=7'
    # Pass missing kwd arg as positional arg:
    assert f_no_kwargs(..., b=5, c=...)(3, 7) == 'a=3, b=5, c=7'
    # Test recursion of partially_applicable:
    assert f_no_kwargs(..., ..., c=7)(..., 5)(3) == 'a=3, b=5, c=7'
    assert f_no_kwargs(..., 5, c=...)(..., c=7)(3) == 'a=3, b=5, c=7'
    assert f_no_kwargs(3, ..., ...)(5, ...)(7) == 'a=3, b=5, c=7'
