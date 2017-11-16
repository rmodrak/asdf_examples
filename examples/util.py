
# this module exists solely for convenience
# eventually, many utilities will be moved elsewhere


import os


def dirname(filename):
    return os.path.abspath(os.path.dirname(filename))


def event_stats(ds):
    origin = ds.events[0].preferred_origin()
    return origin.latitude, origin.longitude, origin.time


def is_mpi_env():
    """
    Test if current environment is MPI or not
    """
    try:
        import mpi4py
    except ImportError:
        return False

    try:
        import mpi4py.MPI
    except ImportError:
        return False

    return True


def setup_mpi():
    if not is_mpi_env():
        raise EnvironmentError("MPI environment required for parallel processing.")
                                                                                    
