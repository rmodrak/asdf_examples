#!/usr/bin/env python

import pytomo3d.adjoint
import pyasdf
import pyadjoint

from os.path import join
from util import dirname, read_json_mpi, Struct


# for consistency, filter parameters used here
# must match those in asdf_examples/process_traces.py
filter_parameters = {
    'interp_flag': True,
    'interp_delta': 0.1425,
    'interp_npts': 42000,
    'sum_over_comp_flag': False,
    'weight_flag': False,
    'filter_flag': True,
    'pre_filt': [0.0067, 0.01, 0.02, 0.025],
    'taper_type': "hann",
    'taper_percentage': 0.05,
    'add_missing_comp_flag': False,
    'rotate_flag': False,
    }


# see pyadjoint documentation for parameter descriptions
misfit_parameters = {
    #'adj_src_type': "multitaper_misfit",
    'min_period': 50.0,
    'max_period': 100.0,
    'lnpt': 15,
    'transfunc_waterlevel': 1.0E-10,
    'water_threshold': 0.02,
    'ipower_costaper': 10,
    'min_cycle_in_window': 3,
    'taper_percentage': 0.3,
    'mt_nw': 4.0,
    'num_taper': 5,
    'phase_step': 1.5,
    'dt_fac': 2.0,
    'err_fac': 2.5,
    'dt_max_scale': 3.5,
    'measure_type': 'dt',
    'taper_type': 'hann',
    'dt_sigma_min': 1.0,
    'dlna_sigma_min': 0.5,
    'use_cc_error': True,
    'use_mt_error': False,
    }


misfit_type = 'multitaper_misfit'


paths = Struct({
    'obs' : '../data/C200912240023A.obs_bp.h5',
    'syn' : '../data/C200912240023A.syn_bp.h5',
    'windows' : '../data/C200912240023A.windows.json',
    })


if __name__=='__main__':
    # this example must be invoked with MPI
    # e.g. mpiexec -np NP multitaper_misfit.py
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    rank = comm.rank

    cwd = dirname(__file__)

    # read data
    fullpath = join(cwd, paths.obs)
    obs = pyasdf.ASDFDataSet(fullpath, compression=None, mode="a")
    event = obs.events[0]

    # read syntheics
    fullpath = join(cwd, paths.syn)
    syn = pyasdf.ASDFDataSet(fullpath, compression=None, mode="a")

    # read windows
    fullpath = join(cwd, paths.windows)
    windows = read_json_mpi(paths.windows, comm)

    # generate pyadjoint.Config objects
    config = pyadjoint.Config(**misfit_parameters)

    # wrapper is required for ASDF processing
    def wrapped_function(obs_, syn_):
        obs_traces = getattr(obs_, 'processed')
        syn_traces = getattr(syn_, 'processed')
        # TODO: modify pytomo3d to make the following
        # function call more readable
        return pytomo3d.adjoint.calculate_and_process_adjsrc_on_stream(
            obs_traces, syn_traces, windows[obs_._station_name],
            obs_.StationXML, config, event,
            misfit_type, filter_parameters,
            figure_mode=False, figure_dir=None)

    # evaluate misfit
    adjoint_sources = obs.process_two_files_without_parallel_output(
        syn, wrapped_function)

    # save results
    if rank==0:
        print adjoint_sources

