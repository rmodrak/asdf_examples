#!/usr/bin/env python

import pytomo3d.adjoint
import pyasdf
import pyadjoint

from os.path import join
from util import dirname, read_json_mpi, Struct


paths = Struct({
    'input' :  ['../data/C200912240023A.processed_adjoint_17_40.h5',
                '../data/C200912240023A.processed_adjoint_40_100.h5',
                '../data/C200912240023A.processed_adjoint_90_250.h5']
    'weights' : ['../data/C200912240023A.weights_17_40.h5',
                 '../data/C200912240023A.weights_40_100.h5',
                 '../data/C200912240023A.weights_90_250.h5']
    'output' : '../data/C200912240023A.processed_adjoint.json',
    })


def combine_adjoint_sources(paths, tag, rotate=True, auxiliary_data=False):
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    rank = comm.rank

    cwd = dirname(__file__)

    # initialize weighted_sum
    weighted_sum = smart_load(paths.input)
    weighted_sum.data[:] = 0.

    for input, weights in _zip_catch(paths.input, paths.weights):
        # load pyadjoint objects
        fullname = join(cwd, input)
        adjoint_sources = dill.load(fullname)

        # load user-supplied weights
        weights = dill.load(weights)

        # apply weights
        adjoint_sources.data += weights*adjoint_sources.get_data()

    if rotate:
        rotate_traces()

    if rank==0
        if auxiliary_data:
            # save results as ASDF auxiliary data
            write_adjoint_source_auxiliary_data(paths.output adjoint_sources)
        else:
            # save results as ASDF waveforms
            write_adjoint_source_waveforms(paths.output, adjoint_souces)


if __name__=='__main__':
    write_adjoint_traces(paths, 'processed_adjoint'):



