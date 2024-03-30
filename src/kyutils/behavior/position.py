import os
import numpy as np
from ..spikegadgets.trodesconf import readTrodesExtractedDataFile
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import pandas as pd


def load_position_from_rec(rec_directory):
    """Load position data from online tracking saved with rec file.

    Parameters
    ----------
    rec_directory : str
        path where the rec file (along with videoPositionTracking and videoTimeStamps.cameraHWSync files live)

    Returns
    -------
    position_array : numpy.ndarray[float], (frames, dimensions)
    position_timestamps_ptp : np.array
        timestamp for position of the marker detected in each frame of the video, in PTP time (seconds)
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
    """Plots the position of the animal when the given neuron fired a spike.

    Parameters
    ----------
    spike_times : numpy.ndarray[float]
        Array of spike times
    position : numpy.ndarray[float], (frames, dimensions)
        Array of position
    t_position : numpy.ndarray[float]
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


# fig, ax = plt.subplots(21)


def position_raster2(
    sorting, unit_id, predict_epoch, color1="b", color2="r", ax1=None, ax2=None
):
    sorting = sorting.frame_slice(
        start_frame=epoch_frame_start[predict_epoch],
        end_frame=epoch_frame_end[predict_epoch],
    )
    decode_timestamps_ephys = (
        timestamps_ephys[predict_epoch] - timestamps_ephys[predict_epoch][0]
    )
    spike_times = decode_timestamps_ephys[
        sorting.get_unit_spike_train(
            unit_id,
        )
    ]

    linearized_position, t_position = get_position_interp(predict_epoch)

    invalid_position_ind = (
        ((linearized_position > 71) & (linearized_position <= (71 + 15)))
        | (
            (linearized_position > (71 + 15 + 32))
            & (linearized_position <= (71 + 15 + 32 + 15))
        )
        | (
            (linearized_position > (71 + 15 + 32 + 15 + 71))
            & (linearized_position <= (71 + 15 + 32 + 15 + 71 + 15))
        )
        | (
            (linearized_position > (71 + 15 + 32 + 15 + 71 + 15 + 32))
            & (linearized_position <= (71 + 15 + 32 + 15 + 71 + 15 + 32 + 15))
        )
    )

    linearized_position = linearized_position[~invalid_position_ind]
    t_position = t_position[~invalid_position_ind]

    _, is_inbound = get_trajectory_direction(linearized_position)

    t_position_inbound = t_position[is_inbound]
    t_position_outbound = t_position[~is_inbound]
    linearized_position_inbound = linearized_position[is_inbound]
    linearized_position_outbound = linearized_position[~is_inbound]

    inds = np.searchsorted(t_position, spike_times)
    inds[inds == len(t_position)] = len(t_position) - 1
    inds_inbound = np.searchsorted(t_position_inbound, spike_times)
    inds_inbound[inds_inbound == len(t_position_inbound)] = len(t_position_inbound) - 1
    inds_outbound = np.searchsorted(t_position_outbound, spike_times)
    inds_outbound[inds_outbound == len(t_position_outbound)] = (
        len(t_position_outbound) - 1
    )

    if (ax1 is None) and (ax2 is None):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 5), sharey=True, sharex=True)
    # ax[0].plot(linearized_position, t_position, 'gray', linestyle='dotted',alpha=0.1)
    # ax[0].plot(linearized_position[inds],t_position[inds], 'k|', markersize=1)

    ax1.plot(
        linearized_position_inbound,
        t_position_inbound,
        "gray",
        linestyle="-",
        alpha=0.1,
    )
    ax1.plot(
        linearized_position_inbound[inds_inbound],
        t_position_inbound[inds_inbound],
        "|",
        color=color1,
        markersize=1,
    )

    ax2.plot(
        linearized_position_outbound,
        t_position_outbound,
        "gray",
        linestyle="-",
        alpha=0.1,
    )
    ax2.plot(
        linearized_position_outbound[inds_outbound],
        t_position_outbound[inds_outbound],
        "|",
        color=color2,
        markersize=1,
    )

    # ax[0].plot(linearized_position, t_position, 'gray', linestyle='dotted',alpha=0.1)
    # ax[0].plot(linearized_position_inbound[inds_inbound],t_position_inbound[inds_inbound], 'b|', markersize=1)
    # ax[0].plot(linearized_position_outbound[inds_outbound],t_position_outbound[inds_outbound], 'r|', markersize=1)

    alpha = 0.2
    color = "gray"
    # ax[2].axvspan(71, 71+15, color=color, alpha=alpha)
    # ax[2].axvspan(71+15+32, 71+15+32+15, color=color, alpha=alpha)
    # ax[2].axvspan(71+15+32+15+71, 71+15+32+15+71+15, color=color, alpha=alpha)
    # ax[2].axvspan(71+15+32+15+71+15+32, 71+15+32+15+71+15+32+15, color=color, alpha=alpha)

    ax2.axvspan(71, 71 + 15, color=color, alpha=alpha)
    ax2.axvspan(71 + 15 + 32, 71 + 15 + 32 + 15, color=color, alpha=alpha)
    ax2.axvspan(
        71 + 15 + 32 + 15 + 71, 71 + 15 + 32 + 15 + 71 + 15, color=color, alpha=alpha
    )
    ax2.axvspan(
        71 + 15 + 32 + 15 + 71 + 15 + 32,
        71 + 15 + 32 + 15 + 71 + 15 + 32 + 15,
        color=color,
        alpha=alpha,
    )

    ax1.axvspan(71, 71 + 15, color=color, alpha=0.2)
    ax1.axvspan(71 + 15 + 32, 71 + 15 + 32 + 15, color=color, alpha=0.2)
    ax1.axvspan(
        71 + 15 + 32 + 15 + 71, 71 + 15 + 32 + 15 + 71 + 15, color=color, alpha=0.2
    )
    ax1.axvspan(
        71 + 15 + 32 + 15 + 71 + 15 + 32,
        71 + 15 + 32 + 15 + 71 + 15 + 32 + 15,
        color=color,
        alpha=0.2,
    )

    # ax[0].plot(linearized_position_cm, place_fields[:,unit_id]*2000,)

    # ax.plot([0,71], [0,0], 'r')
    # ax.plot([71+15,71+15+32], [0,0], 'r')

    # ax[0].set_title('unit_id: '+str(unit_id)+', epoch: '+predict_epoch)
    # ax[1].set_xlabel('Position (cm)')
    # ax[0].set_ylabel('Time (s)')
    ax2.set_title("Outbound")
    ax1.set_title("Inbound")
    # ax[0].set_title('Combined')

    return (ax1, ax2)


def get_trajectory_direction(linear_distance):
    is_inbound = np.insert(np.diff(linear_distance) < 0, 0, False)
    return np.where(is_inbound, "Inbound", "Outbound"), is_inbound


def get_position_from_dlc(
    path_to_dlc_h5,
    dlc_tag,
    body_part,
    t_position,
    pixels_to_cm=5.3,
    offset=10,
    position_time_bin=2e-3,
):

    df = pd.read_hdf(path_to_dlc_h5)

    x = df[(dlc_tag, body_part, "x")].to_numpy()
    y = df[(dlc_tag, body_part, "y")].to_numpy()

    position = np.column_stack((x, y))

    position = position[offset:] / pixels_to_cm

    position_sampling_rate = len(t_position) / (t_position[-1] - t_position[0])
    start_time = t_position[0]
    end_time = t_position[-1]
    sampling_rate = int(1 / position_time_bin)
    n_samples = int(np.ceil((end_time - start_time) * sampling_rate)) + 1

    time = np.linspace(start_time, end_time, n_samples)

    max_plausible_speed = (100.0,)
    position_smoothing_duration = 0.125
    speed_smoothing_std_dev = 0.100
    orient_smoothing_std_dev = 0.001
    upsampling_interpolation_method = "linear"

    import position_tools as pt

    speed = pt.get_speed(
        position,
        t_position,
        sigma=speed_smoothing_std_dev,
        sampling_frequency=position_sampling_rate,
    )

    is_too_fast = speed > max_plausible_speed
    position[is_too_fast] = np.nan

    position = pt.interpolate_nan(position)

    return position, time


def linearize_position(
    position, node_positions, edges, linear_edge_order, linear_edge_spacing
):
    """Linearize and interpolate position

    Parameters
    ----------
    node_positions : _type_
        _description_
    edges : _type_
        _description_
    linear_edge_order : _type_
        _description_
    linear_edge_spacing : _type_
        _description_

    Example (W-track)
    -----------------
    node_positions = np.array(
        [
            (55, 81),  # center well
            (23, 81),  # left well
            (87, 81),  # right well
            (55, 10),  # center junction
            (23, 10),  # left junction
            (87, 10),  # right junction
        ]
    )

    edges = np.array(
        [
            (0, 3),
            (3, 4),
            (3, 5),
            (4, 1),
            (5, 2),
        ]
    )

    linear_edge_order = [
        (0, 3),
        (3, 4),
        (4, 1),
        (3, 5),
        (5, 2),
    ]
    linear_edge_spacing = 15
    """
    import track_linearization as tl

    track_graph = tl.make_track_graph(node_positions, edges)

    position_df = tl.get_linearized_position(
        position=position,
        track_graph=track_graph,
        edge_order=linear_edge_order,
        edge_spacing=linear_edge_spacing,
    )

    return position_interp


def interpolate_position(position_df, t_position, time):
    import scipy

    f_pos = scipy.interpolate.interp1d(
        t_position,
        position_df["linear_position"],
        axis=0,
        bounds_error=False,
        kind="linear",
    )
    position_interp = f_pos(time)

    return position_interp, time


def plot_place_fields_heatmap(place_fields, sorted_indices=None, ax=None):
    if sorted_indices is None:
        max_indices = np.nanargmax(place_fields, axis=0)
        sorted_indices = np.argsort(max_indices)
    place_field_permuted = place_fields[:, sorted_indices]
    # place_field_permuted = place_field_permuted[:, ~np.isnan(place_field_permuted).any(axis=0)]
    place_field_permuted = place_field_permuted[
        :, np.sum(place_field_permuted, axis=0) != 0
    ]

    place_field_permuted_normalized = place_field_permuted / np.nanmax(
        place_field_permuted, axis=0
    )

    if ax is None:
        return sorted_indices
        # fig, ax = plt.subplots(figsize=(10,10))
    im = ax.imshow(place_field_permuted_normalized.T, aspect="auto")
    ax.set_xlabel("Position (bins)")
    ax.set_ylabel("Neurons")
    return sorted_indices, im
