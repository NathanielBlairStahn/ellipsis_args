from loguru import logger

SENTINEL = Ellipsis

# Original no kwargs version from 2022-11-05.
# This version has been spot tested but not rigorously tested.
def partially_applicable_no_kwargs(func, nullary_as_const=True):
    def partially_applicable_func_no_kwargs(*args):
        # This list maps the index of each new argument to its original position in args
        omitted_indices = [j for j, arg in enumerate(args) if arg is SENTINEL]
#   This works, but then we don't have the option to return a function rather than a constant:
#         if len(omitted_indices) == 0:
#             return func(*args) # Nullary function because arity equals number of omitted indices
        logger.debug(f"{omitted_indices=}")
        def partially_applied_func(*fewer_args):
            logger.debug(f"{omitted_indices=}, {args=}, {fewer_args=}")
            if len(fewer_args) != len(omitted_indices):
                raise TypeError(
                    f"The partially applied function takes {len(omitted_indices)} "
                    f"positional arguments, but {len(fewer_args)} were given"
                )
            new_args = list(args)
            for i,j in enumerate(omitted_indices):
                new_args[j] = fewer_args[i]
            logger.debug(f"{new_args=}")
            return func(*new_args)

        if len(omitted_indices) == 0:
            # Base case: Don't recurse when result is nullary
            return partially_applied_func() if nullary_as_const else partially_applied_func
        else:
            # If not nullary, use recursion to get another partially applicable function
            return partially_applicable_no_kwargs(partially_applied_func)

    return partially_applicable_func_no_kwargs

# Original version from 2022-11-06 allowing kwargs as well as args.
# This function also has not been rigorously tested.
# This version has a known bug where keyword arguments in the
# original function cannot be passed as positional arguments
# in the partially applied function.
# Also, positional arguments in the original function cannot be passed
# as keyword arguments in the partially applied function because
# adding this functionality requires more complexity, namely, I think
# we would need the inspect module to find out what the names of the
# original positional arguments were.
def partially_applicable(func, nullary_as_const=True):
    def partially_applicable_func(*args, **kwargs):
        # This list maps the index of each new argument to its original position in args
        omitted_indices = [j for j, arg in enumerate(args) if arg is SENTINEL]
        omitted_kwds = [kwd for kwd, val in kwargs.items() if val is SENTINEL]
        logger.debug(f"{omitted_indices=}, {omitted_kwds=}")

        def partially_applied_func(*fewer_args, **fewer_kwargs):
            logger.debug(f"{omitted_indices=}, {args=}, {fewer_args=}")
            logger.debug(f"{omitted_kwds=}, {kwargs=}, {fewer_kwargs=}")
            if (n_given:=len(fewer_args)+len(fewer_kwargs)) != (n_required:=len(omitted_indices)+len(omitted_kwds)):
                raise TypeError(
                    f"The partially applied function takes {n_required} "
                    f"arguments, but {n_given} were given"
                )
            new_args, new_kwargs = list(args), dict(kwargs)

            for i,j in enumerate(omitted_indices):
                new_args[j] = fewer_args[i]
            for kwd in omitted_kwds:
                new_kwargs[kwd] = fewer_kwargs[kwd]
            logger.debug(f"{new_args=}, {new_kwargs=}")
            return func(*new_args, **new_kwargs)

        if len(omitted_indices) == 0 and len(omitted_kwds) == 0:
            # Base case: Don't recurse when result is nullary
            return partially_applied_func() if nullary_as_const else partially_applied_func
        else:
            # If not nullary, use recursion to get another partially applicable function
            return partially_applicable(partially_applied_func)

    return partially_applicable_func
