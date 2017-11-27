#!/usr/bin/env python

### this script must be invoked with MPI
### e.g. mpiexec -n NP process_traces.py


import pytomo3d.signal
import pyasdf

from os.path import join
from util import dirname, event_stats, Struct


parameters_obs = {
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


parameters_syn = {
    'remove_response_flag': False,
    'filter_flag': True,
    'pre_filt': [0.0067, 0.01, 0.02, 0.025],
    'starttime': 0,
    'endtime': 6000,
    'resample_flag': True,
    'sampling_rate': 5,
    'taper_type': "hann",
    'taper_percentage': 0.05,
    'rotate_flag': True,
    'sanity_check': False,
    }


paths_obs = Struct({
    'input' : '../data/C200912240023A.observed.h5',
    'output' : '../data/C200912240023A.processed_observed.h5',
    })


paths_syn = Struct({
    'input' : '../data/C200912240023A.synthetic.h5',
    'output' : '../data/C200912240023A.processed_synthetic.h5',
    })


def process_traces(parameters, paths, tag1, tag2):
    from mpi4py import MPI

    cwd = dirname(__file__)

    # read data
    fullpath = join(cwd, paths.input)
    ds = pyasdf.ASDFDataSet(fullpath, compression=None, mode="a")
    event = ds.events[0]

    # add event information
    latitude, longitude, origin_time = event_stats(ds)
    parameters['event_longitude'] = longitude
    parameters['event_latitude'] = latitude
    parameters['starttime'] = origin_time + parameters['starttime']
    parameters['endtime'] = origin_time + parameters['endtime']

    # wrapper is required for ASDF processing
    def wrapped_function(stream, inventory):
        parameters.update({"inventory": inventory})
        return pytomo3d.signal.process_stream(stream, **parameters)

    # process data
    ds.process(wrapped_function,
        paths.output,
        {tag1: tag2})

    del ds


if __name__=='__main__':
    process_traces(parameters_obs, paths_obs, 'observed', 'processed_observed')
    process_traces(parameters_syn, paths_syn, 'synthetic', 'processed_synthetic')

