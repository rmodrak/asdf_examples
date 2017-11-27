
# this module exists for temporary convenience
# eventually, utilities will be moved to pytomo3d

import copy
import json
import os


def dirname(filename):
    return os.path.abspath(os.path.dirname(filename))


def event_stats(ds):
    origin = ds.events[0].preferred_origin()
    return origin.latitude, origin.longitude, origin.time


def write_windows_json(filename, unparsed):
    from pytomo3d.window.io import get_json_content, WindowEncoder

    # create nested dictionaries
    parsed = {}
    for station, traces in _items(unparsed):
        parsed[station] = {}
        for trace, windows in _items(traces):
            parsed[station][trace] = []

    # fill in dictionaries
    for station, traces in _items(unparsed):
        for trace, windows in _items(traces):
            for window in windows:
                parsed[station][trace] += [get_json_content(window)]

    # write dictionaries to json
    with open(filename, 'w') as fh:
        fh.write(json.dumps(parsed,
            cls=WindowEncoder, sort_keys=True,
            indent=2, separators=(',', ':')))


def _items(dict1):
    dict2 = copy.deepcopy(dict1)
    for key,val in dict1.iteritems():
        if not val: dict2.pop(key)
    return dict2.iteritems()


def read_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def read_json_mpi(filename, comm):
    rank = comm.Get_rank()
    obj = None
    if rank == 0:
        obj = read_json(filename)
    return comm.bcast(obj, root=0)


class Struct(dict):
    def __init__(self, *args, **kwargs):
        super(Struct, self).__init__(*args, **kwargs)
        self.__dict__ = self


def add_adjoint_source_waveforms(ds, adjoint_sources, tag):
    import obspy

    for adjoint_source in adjoint_sources.values():
        data = []
        for window in adjoint_source:
            data += [window.adjoint_source]

        trace = obspy.core.trace.Trace(sum(data),
            header=obspy.core.trace.Stats({
                'network':window.network,
                'station':window.station,
                'location':window.location,
                'starttime':window.starttime,
                'sampling_rate':window.dt}))

        ds.add_waveforms(trace, tag)


def add_adjoint_source_auxiliary_data(ds, adjoint_sources):
    for station, channels in adjoint_sources.items():
        for adjoint_source in channels:
            adjoint_source.write_asdf(ds)

