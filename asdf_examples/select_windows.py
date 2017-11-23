#!/usr/bin/env python

import pytomo3d.window
import pyasdf
import pyflex

from os.path import join
from util import dirname, write_windows_json, Struct


# see FLEXWIN manual for parameter descriptions
flexwin_parameters = {
    "min_period": 50.0,
    "max_period": 100.0,
    "stalta_waterlevel": 0.10,
    "tshift_acceptance_level": 8.0,
    "tshift_reference": 0.0,
    "dlna_acceptance_level": 0.50,
    "dlna_reference": 0.0,
    "cc_acceptance_level": 0.90,
    "s2n_limit": 3.0,
    #"s2n_limit_energy": 1.5,
    "window_signal_to_noise_type": "amplitude",
    #"selection_mode": "body_waves",
    #"min_surface_wave_velocity": 3.20,
    #"max_surface_wave_velocity": 4.10,
    "earth_model": "ak135",
    #"max_time_before_first_arrival": 50.0,
    #"max_time_after_last_arrival": 100.0,
    "check_global_data_quality": True,
    "snr_integrate_base": 3.5,
    "snr_max_base": 3.0,
    "c_0": 0.7,
    "c_1": 2.0,
    "c_2": 0.0,
    "c_3a": 1.0,
    "c_3b": 2.0,
    "c_4a": 3.0,
    "c_4b": 10.0,
    "resolution_strategy": "interval_scheduling",
    }


parameters_by_channel = {
    'BHR': flexwin_parameters,
    'BHT': flexwin_parameters,
    'BHZ': flexwin_parameters,
    }


paths = Struct({
    'obs' : '../data/C200912240023A.processed_observed.h5',
    'syn' : '../data/C200912240023A.processed_synthetic.h5',
    'output' : '../data/C200912240023A.windows.json',
    'log' : '../data/C200912240023A.windows.log',
    })

merge_flag = False


def select_windows(parameters, paths, merge_flag, obs_tag, syn_tag):
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    rank = comm.rank

    cwd = dirname(__file__)

    # read data
    fullpath = join(cwd, paths.obs)
    obs = pyasdf.ASDFDataSet(fullpath, compression=None, mode="a")
    event = obs.events[0]

    # read synthetics
    fullpath = join(cwd, paths.syn)
    syn = pyasdf.ASDFDataSet(fullpath, compression=None, mode="a")

    # generate pyflex.Config objects
    config = {}
    for channel, param in parameters.items():
        config[channel] = pyflex.Config(**param)

    # wrapper is required for ASDF processing
    def wrapped_function(obs, syn):
        return pytomo3d.window.window_on_stream(
            obs[obs_tag], syn[syn_tag], config, station=obs.StationXML,
            event=event, user_modules=None,
            figure_mode=False, figure_dir=None,
            _verbose=False)

    # run window selection
    windows = obs.process_two_files_without_parallel_output(
        syn, wrapped_function)

    # save results
    if rank==0:
        if merge_flag: windows = merge(windows)
        write_windows_json(paths.output, windows)


if __name__=='__main__':
    select_windows(parameters_by_channel, paths, merge_flag, 
        'processed_observed', 'processed_synthetic')
