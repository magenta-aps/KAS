def first_not_none(*args):
    return next(item for item in args if item is not None)
