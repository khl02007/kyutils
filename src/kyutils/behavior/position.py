import os
import numpy as np
from ..spikegadgets.trodesconf import readTrodesExtractedDataFile
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter


def load_position_from_rec(rec_directory):
    """Load position data from online tracking saved with rec file.

    Parameters
    ----------
    rec_directory : str
        path where the rec file (along with videoPositionTracking and videoTimeStamps.cameraHWSync files live)

    Returns
    -------
    position_array :
        _description_
    position_timestamps_ptp :
        timestamp for position of the marker detecte in each frame of the video, in PTP time (seconds)
    """

    online_tracking_file = find_file_with_extension(
        rec_directory, "videoPositionTracking"
    )
    online_tracking_timestamps_file = find_file_with_extension(
        rec_directory, "videoTimeStamps.cameraHWSync"
    )

    position = readTrodesExtractedDataFile(online_tracking_file)
    t_position = readTrodesExtractedDataFile(online_tracking_timestamps_file)

    position_array = np.zeros((len(position["data"]["xloc"]), 2))
    position_array[:, 0] = position["data"]["xloc"]
    position_array[:, 1] = position["data"]["yloc"]

    position_timestamps_ptp = t_position["data"]["HWTimestamp"]

    return (position_array, position_timestamps_ptp)


def plot_spatial_raster(spike_times, position, t_position, ax=None):
    """Plots the position of the animal when the given neuron fired a spike

    Parameters
    ----------
    spike_times : numpy.nadarray[float]
        Array of spike times
    position : numpy.ndarray[float], (frames, dimensions)
        Array of position
    t_position : numpy.nadarray[float]
        Array of timestamps for the position; must be aligned with the spike times
    ax : matplotlib.axes, optional
        The axis on which to plot, by default None

    Returns
    -------
    ax : matplotlib.axes
        The axis object for the plot
    """
    if ax is None:
        fig, ax = plt.subplots()

    ind = np.searchsorted(t_position, spike_times)
    ind = ind[ind < len(position)]

    ax.plot(position[:, 0], position[:, 1], "k", alpha=0.1)
    ax.plot(position[ind, 0], position[ind, 1], "r.", markersize=2.0, alpha=0.7)

    return ax


def bin_spikes_into_position(spike_position, position, bin_size):
    # Determine the minimum and maximum values for x and y
    x_min, x_max = np.min(position[:, 0]), np.max(position[:, 0])
    y_min, y_max = np.min(position[:, 1]), np.max(position[:, 1])

    # Calculate the number of bins in x and y directions
    x_bins = int(np.ceil((x_max - x_min) / bin_size[0]))
    y_bins = int(np.ceil((y_max - y_min) / bin_size[1]))

    # Initialize a 2D array to store the count of points in each bin
    binned_position = np.zeros((x_bins, y_bins), dtype=int)
    binned_spike_position = np.zeros((x_bins, y_bins), dtype=int)

    # Place each point into its appropriate bin
    for x, y in position:
        x_bin = int((x - x_min) // bin_size[0])
        y_bin = int((y - y_min) // bin_size[1])

        # Increment the count for the bin that this point belongs to
        binned_position[x_bin, y_bin] += 1

    for x, y in spike_position:
        x_bin = int((x - x_min) // bin_size[0])
        y_bin = int((y - y_min) // bin_size[1])

        # Increment the count for the bin that this point belongs to
        binned_spike_position[x_bin, y_bin] += 1

    return binned_spike_position, binned_position


def plot_place_field(
    spike_times, position, t_position, bin_size=[10, 10], sigma=1, ax=None
):
    """Plots occupancy normalized place field

    Parameters
    ----------
    spike_times : array_like
        Timing of spikes
    position : array_like
        Position, (frames, 2)
    t_position : array_like
        Timestamp of the position
    bin_size : list, optional
        Size of the spatial bin ([x, y]); must be the same unit as the position (e.g. pixels), by default [10,10]
    sigma : int, optional
        The standard deviation of the Gaussian kernel for smoothing, by default 1
    ax : matplotlib.axes object, optional
        The axis object for the plot, by default None

    Returns
    -------
    ax : matplotlib.axes
        The axis object for the plot
    """
    if ax is None:
        fig, ax = plt.subplots()
    ind = np.searchsorted(t_position, spike_times)
    ind = ind[ind < len(position)]
    spike_position = position[ind]

    binned_spike, binned_pos = bin_spikes_into_position(
        spike_position, position, bin_size
    )

    array = np.rot90(binned_spike / binned_pos, 1)
    array_no_nan = np.nan_to_num(array)

    # Apply Gaussian smoothing
    smoothed_array = gaussian_filter(array_no_nan, sigma)

    # Put NaNs back to their original positions
    smoothed_array_with_nan = np.where(np.isnan(array), np.nan, smoothed_array)

    ax.imshow(smoothed_array_with_nan, cmap="hot", interpolation="nearest")
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
