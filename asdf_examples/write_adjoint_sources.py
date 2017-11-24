#!/usr/bin/env python

import dill as pickle
import json

import pytomo3d.adjoint
import pyasdf
import pyadjoint

from os.path import join
from util import dirname, read_json_mpi, Struct
from util import add_adjoint_source_waveforms, add_adjoint_source_auxiliary_data


misfit_type = 'multitaper_misfit'

# see pyadjoint documentation for parameter descriptions
misfit_parameters = {
    #adj_src_type': "multitaper_misfit",
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


paths = Struct({
    'obs' : '../data/C200912240023A.processed_observed.h5',
    'syn' : '../data/C200912240023A.processed_synthetic.h5',
    'windows' : '../data/C200912240023A.windows.json',
    'misfit' : '../data/C200912240023A.misfit.json',
    'adjoint_sources' : '../data/C200912240023A.adjoint_sources.h5',
    })


def write_adjoint_traces(misfit_type, misfit_parameters, filter_parameters, paths,
                    obs_tag, syn_tag): 
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

    # read windows
    fullpath = join(cwd, paths.windows)
    windows = read_json_mpi(paths.windows, comm)

    # generate pyadjoint.Config objects
    config = pyadjoint.Config(**misfit_parameters)

    # wrapper is required for ASDF processing
    def wrapped_function(obs, syn):
        # TODO: modify pytomo3d to make the following
        # function call more readable?
        return pytomo3d.adjoint.calculate_and_process_adjsrc_on_stream(
            obs[obs_tag], syn[syn_tag], windows[obs._station_name],
            obs.StationXML, config, event,
            misfit_type, filter_parameters,
            figure_mode=False, figure_dir=None)

    adjoint_sources = obs.process_two_files_without_parallel_output(
        syn, wrapped_function)

    if rank==0:
        # save as ASDF waveforms
        ds = pyasdf.ASDFDataSet(paths.adjoint_sources, mpi=False, mode="a")
        tag = 'processed_adjoint'
        if rank==0: add_adjoint_source_waveforms(ds, adjoint_sources, event, tag)
        del ds

        # write misfit
        pass



if __name__=='__main__':
    write_adjoint_traces(misfit_type, misfit_parameters, filter_parameters, paths, 
        'processed_observed', 'processed_synthetic')

