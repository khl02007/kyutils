import os
import numpy as np
from ..spikegadgets.trodesconf import readTrodesExtractedDataFile
import matplotlib.pyplot as plt

def load_position_from_rec(rec_directory):

    online_tracking_file = find_file_with_extension(rec_directory, 'videoPositionTracking')
    online_tracking_timestamps_file = find_file_with_extension(rec_directory, 'videoTimeStamps.cameraHWSync')

    position = readTrodesExtractedDataFile(online_tracking_file)
    t_position = readTrodesExtractedDataFile(online_tracking_timestamps_file)

    position_array = np.zeros((len(position['data']['xloc']),2))
    position_array[:,0] = position['data']['xloc']
    position_array[:,1] = position['data']['yloc']
    
    position_timestamps_ptp = t_position['data']['HWTimestamp']
    
    return (position_array, position_timestamps_ptp)

def plot_spatial_raster(spike_times, position, t_position, ax=None):
    if ax is None:
        fig, ax = plt.subplots()
        
    ind = np.searchsorted(t_position, spike_times)
    ind = ind[ind<len(position)]
    
    ax.plot(position[:,0], position[:,1], 'k', alpha=0.1)
    ax.plot(position[ind,0], position[ind,1], 'r.', markersize=2., alpha=0.7)
    
    return ax

def find_file_with_extension(directory, extension):
    """
    Searches for a file with a particular extension in a directory and returns its path.

    Parameters:
    - directory (str): The directory to search in.
    - extension (str): The extension to look for (e.g., '.txt').

    Returns:
    - The full path of the first file found with the specified extension, or None if no such file exists.
    """
    for filename in os.listdir(directory):
        if filename.endswith(extension):
            return os.path.join(directory, filename)
    return None