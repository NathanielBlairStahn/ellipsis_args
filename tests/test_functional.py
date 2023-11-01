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

@partially_applicable
def h(a, b, *args, c=1, d=2, **kwargs):
    return f'{a=}, {b=}, {args=}, {c=}, {d=}, {kwargs=}'

def test_f_no_kwargs():
    assert f_no_kwargs(3, 5, 7) == 'a=3, b=5, c=7'
    assert f_no_kwargs(..., 5, 7)(3) == 'a=3, b=5, c=7'
    assert f_no_kwargs(3, ..., 7)(5) == 'a=3, b=5, c=7'
    assert f_no_kwargs(3, ..., ...)(5, 7) == 'a=3, b=5, c=7'
    assert f_no_kwargs(..., 5, ...)(3, 7) == 'a=3, b=5, c=7'
    assert f_no_kwargs(..., ..., ...)(3, 5, 7) == 'a=3, b=5, c=7'
    assert f_no_kwargs(..., ..., c=7)(3, 5) == 'a=3, b=5, c=7'
    assert f_no_kwargs(..., b=5, c=7)(3) == 'a=3, b=5, c=7'

def test_f_no_kwargs_kwd_vs_pos():
    # Raises SyntaxError: positional argument follows keyword argument
    # since ... comes after b=5. This happens on compilation, so can't run:
    # assert f_no_kwargs(..., b=5, ...)(3, 7) == 'a=3, b=5, c=7'
    assert f_no_kwargs(..., b=5, c=...)(3, c=7) == 'a=3, b=5, c=7'
    # Pass missing kwd arg as positional arg:
    assert f_no_kwargs(..., b=5, c=...)(3, 7) == 'a=3, b=5, c=7'
    assert f_no_kwargs(a=..., b=5, c=...)(3, 7) == 'a=3, b=5, c=7'

def test_f_no_kwargs_recursion():
    # Test recursion of partially_applicable:
    assert f_no_kwargs(..., ..., c=7)(..., 5)(3) == 'a=3, b=5, c=7'
    assert f_no_kwargs(..., 5, c=...)(..., c=7)(3) == 'a=3, b=5, c=7'
    assert f_no_kwargs(3, ..., ...)(5, ...)(7) == 'a=3, b=5, c=7'
    assert f_no_kwargs(..., ..., ...)(3, ..., ...)(..., 7)(5) == \
        'a=3, b=5, c=7'
    assert f_no_kwargs(..., b=..., c=...)(3, ..., c=...)(..., 7)(5) == \
        'a=3, b=5, c=7'

def test_f():
    # def f(a, b, c, d=1, e=2): return f'{a=}, {b=}, {c=}, {d=}, {e=}'
    assert f(..., 2, ..., 4, e=...)(1, 3, 5) == 'a=1, b=2, c=3, d=4, e=5'
    assert f(..., 2, ..., 4, e=...)(1, 3, e=5) == 'a=1, b=2, c=3, d=4, e=5'
    assert f(..., 2, ..., d=..., e=...)(1, 3, d=4, e=5) == \
        'a=1, b=2, c=3, d=4, e=5'
    assert f(..., 2, ..., d=..., e=...)(1, 3, e=5, d=4) == \
        'a=1, b=2, c=3, d=4, e=5'

@pytest.mark.xfail(reason="passing omitted positional args as kwds not implemented yet")
def test_f_pos_as_kwd():
    assert f(..., 2, ..., 4, e=...)(1, c=3, e=5) == 'a=1, b=2, c=3, d=4, e=5'

def test_f_bad_kwd_control():
    with pytest.raises(TypeError) as excinfo:
        f(1, 2, 3, e=5, x=4)
    assert "f() got an unexpected keyword argument 'x'" in str(excinfo.value)

@pytest.mark.xfail(
    raises=IndexError,
    reason="current implementation assumes keywords are valid")
def test_f_bad_kwd():
    with pytest.raises(TypeError) as excinfo:
        f(..., 2, ..., d=..., e=...)(1, 3, e=5, x=4)
    assert "f() got an unexpected keyword argument 'x'" in str(excinfo.value)

@pytest.mark.xfail(
    raises=TypeError,
    reason="current implementation incorrectly raises "
    "TypeError: The partially applied function takes 3 arguments, but 4 were given")
def test_f_overwrite_kwd():
    assert f(..., 2, ..., e=...)(1, 3, e=5, d=12) == 'a=1, b=2, c=3, d=12, e=5'

def test_h_varargs():
    # def h(a, b, *args, c=1, d=2, **kwargs):
    #     return f'{a=}, {b=}, {args=}, {c=}, {d=}, {kwargs=}'
    assert h(..., b=4)(None) == 'a=None, b=4, args=(), c=1, d=2, kwargs={}'
    assert h(5, ..., 3, 2, 1)(4) == \
        'a=5, b=4, args=(3, 2, 1), c=1, d=2, kwargs={}'
    assert h(5, ..., 3, x=123)(4) == \
        "a=5, b=4, args=(3,), c=1, d=2, kwargs={'x': 123}"
    assert h(..., 4, 3, x=123, c=456)(5) == \
        "a=5, b=4, args=(3,), c=456, d=2, kwargs={'x': 123}"
    assert h(5, 4, ..., x=123)(3) == \
        "a=5, b=4, args=(3,), c=1, d=2, kwargs={'x': 123}"
    assert h(5, 4, ..., ..., ..., x=123)(3, 2, 1) == \
        "a=5, b=4, args=(3, 2, 1), c=1, d=2, kwargs={'x': 123}"
    assert h(5, 4, ..., ..., ..., 0, None, x=123)(3, 2, 1) == \
        "a=5, b=4, args=(3, 2, 1, 0, None), c=1, d=2, kwargs={'x': 123}"
    assert h(5, 4, ..., ..., ..., 0, None, ..., x=123)(3, 2, 1, 'yak!') == \
        "a=5, b=4, args=(3, 2, 1, 0, None, 'yak!'), c=1, d=2, kwargs={'x': 123}"
