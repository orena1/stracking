import os
import json

import numpy as np

from ._io import STrackIO
from stracking.containers import STracks


class StIO(STrackIO):
    """Read/write tracking with the native stracking format

    This format has been created for this library to easily read and write data
    stored in the STracks container

    Parameters
    ----------
    file_path: str
        Path of the .st.json file

    """
    def __init__(self, file_path):
        super().__init__(file_path)
        self.stracks = None
        self.indent = None

    def is_compatible(self):
        if self.file_path.endswith('.json'):
            return True
        return False

    def read(self):
        if os.path.getsize(self.file_path) > 0:
            with open(self.file_path) as json_file:
                json_data = json.load(json_file)

        self.stracks = STracks()
        if 'tracks' in json_data:
            self.stracks.data = np.array(json_data['tracks'])
        else:
            raise Exception('StIO reader: no tracks found in the input file')

        if 'properties' in json_data:
            self.stracks.properties = json_data['properties']

        if 'graph' in json_data:
            self.stracks.graph = json_data['graph']

        if 'features' in json_data:
            self.stracks.features = json_data['features']

        if 'scale' in json_data:
            self.stracks.scale = tuple(json_data['scale'])
            if len(self.stracks.scale) < self.stracks.data.shape[0]-1:
                self.stracks.scale = list(np.ones(self.stracks.data.shape[1]-1))

    def write(self, tracks):
        self.stracks = tracks
        json_data = dict()
        json_data['tracks'] = self.stracks.data.tolist()

        json_data['properties'] = dict()
        if self.stracks.properties is not None:
            for key in self.stracks.properties:
                if isinstance(self.stracks.properties[key], list):
                    json_data['properties'][key] = self.stracks.properties[key]
                else:
                    json_data['properties'][key] = self.stracks.properties[key].tolist()

        json_data['graph'] = self.stracks.graph
        json_data['features'] = self.stracks.features
        if self.stracks.scale is not None:
            json_data['scale'] = list(self.stracks.scale)
        else:
            json_data['scale'] = []

        # write the data to file
        with open(self.file_path, 'w') as outfile:
            json.dump(json_data, outfile, indent=self.indent)
