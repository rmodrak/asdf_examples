#!/usr/bin/env python

import os

import pytomo3d.signal
import pyasdf

from util import dirname, setup_mpi, event_stats

from mpi4py import MPI


parameters = {
    'remove_response_flag': True,
    'water_level': 100.0,
    'filter_flag': True,
    'pre_filt': [0.0067, 0.01, 0.02, 0.025],
    'starttime': 0,
    'endtime': 6000,
    'resample_flag': True,
    'sampling_rate': 5,
    'taper_type': "hann",
    'taper_percentage': 0.05,
    'rotate_flag': True,
    'sanity_check': True,
    }


if __name__=='__main__':
    # this example must be invoked with MPI
    # e.g. mpiexec -np NP process_traces_asdf.py
    setup_mpi()

    # specify paths
    path = dirname(__file__)
    filename = os.path.join(path, "../data/C200912240023A.observed.h5")

    # read data set
    ds = pyasdf.ASDFDataSet(filename, compression=None, mode="a")
    latitude, longitude, origin_time = event_stats(ds)

    # add event information
    parameters['event_longitude'] = longitude
    parameters['event_latitude'] = latitude

    parameters['starttime'] = origin_time + parameters['starttime']
    parameters['endtime'] = origin_time + parameters['endtime']

    # wrapper is required for ASDF processing
    def wrapped_function(stream, inventory):
        parameters.update({"inventory": inventory})
        return pytomo3d.signal.process_stream(stream, **parameters)

    # process data set
    ds.process(wrapped_function,
        filename+'.bp',
        {'observed': 'observed_bp_50_100'})
    del ds

