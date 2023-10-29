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
    assert f_no_kwargs(..., 8, 4)(90) == 'a=90, b=8, c=4'
    assert f_no_kwargs(5, ..., 12)(47) == 'a=5, b=47, c=12'
    assert f_no_kwargs(3, ..., ...)(2, 8) == 'a=3, b=2, c=8'
    assert f_no_kwargs(..., 3, ...)(2, 8) == 'a=2, b=3, c=8'
