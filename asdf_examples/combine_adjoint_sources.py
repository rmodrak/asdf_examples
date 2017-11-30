#!/usr/bin/env python


### DO NOT INVOKE WITH MPI
### Unlike the other scripts in asdf_examples, this one is meant to be invoked
### without MPI, e.g. ./combine_adjoint_sources.py

import copy
import json
import shutil

import pytomo3d.adjoint
import pyasdf
import pyadjoint

from os.path import join
from util import dirname, read_json, Struct, zip_catch
from util import add_adjoint_source_waveforms, add_adjoint_source_auxiliary_data


paths = Struct({
    'input' :  ['../data/C200912240023A.adjoint_sources.h5',],
                #'../data/C200912240023A.processed_adjoint_40_100.h5',
                #'../data/C200912240023A.processed_adjoint_90_250.h5']
    'weights' : ['../data/C200912240023A.weights.json',],
                 #'../data/C200912240023A.weights_sw.h5',
    'output' : '../data/C200912240023A.adjoint_sources_sum.h5',
    })



def combine_adjoint_sources(paths, tag, rotate=True, auxiliary_data=False):
    """ 
    Sums adjoint sources from different ASDF files in a linear combination with
    user-supplied weights. Can be useful, for example, if previous data 
    processing, window selection, and misfit measurements steps were carried out
    separately for different pass bands (e.g. long period, short period) or 
    different phases (e.g. body waves, surface waves).

    param paths.input: ASDF files containing adjoint sources
    type paths.input: list
    param paths.weight: corresponding list of JSON files containing weights
    type paths.weight: list
    param paths.output: summed adjoint sources are written to this ASDF file
    type paths.output: str
    """

    cwd = dirname(__file__)

    adjoint_sources_all = []
    weights_all = []

    for filenames in zip_catch(paths.input, paths.weights):
        # read adjoint sources
        fullname = join(cwd, filenames[0])
        adjoint_sources_all += [pyasdf.ASDFDataSet(fullname, mpi=False, mode='r')]

        # read user-supplied weights
        fullname = join(cwd, filenames[1])
        weights_all += [read_json(fullname)]


    # create output file
    shutil.copy(paths.input[0], paths.output)
    adjoint_sources_sum = pyasdf.ASDFDataSet(paths.output, mpi=False, mode="a")

    # overwite output file data with zeros
    for waveform in adjoint_sources_sum.waveforms:
        for trace in waveform[tag]:
            trace.data[:] = 0.

    # weighted sum of adjoint sources
    for weights, adjoint_sources in zip(weights_all, adjoint_sources_all):
        for station in weights:
            for trace1, trace2 in \
                zip(adjoint_sources_sum.waveforms[station][tag],
                    adjoint_sources.waveforms[station][tag]):
                trace1.data += weights[station][trace1.id]*trace2.data

    # write misfit
    pass



if __name__=='__main__':
    combine_adjoint_sources(paths, 'processed_adjoint')


