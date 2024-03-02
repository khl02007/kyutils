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


def plot_place_fields_ratemap(
    brain_area, epoch, direction, unit_id, ax=None, color="red", alpha=1
):
    classifier = rtc.SortedSpikesClassifier.load_model(
        filename=f"/nimbus/kyu/L10/20231006/run_epochs/classifier_{brain_area}_nn0.1_1d_{epoch}_direction_fit.pkl"
    )
    place_fields = classifier.place_fields_[("", direction)].values / 0.002
    linearized_position = classifier.place_fields_[("", direction)].position.values
    if ax is None:
        fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(linearized_position, place_fields[:, unit_id], color=color, alpha=alpha)
    # ax.set_xlabel("Linearized position (cm)")
    # ax.set_ylabel('P(spike|position)')


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


def get_position_interp(predict_epoch):

    path_to_position = f"/cumulus/kyu/L10/20231006/dlc/L10-20231006-phil-2023-10-26/videos/{predict_epoch}DLC_resnet50_L10-20231006Oct26shuffle1_1230000_filtered.h5"

    df = pd.read_hdf(path_to_position)

    x = df[("DLC_resnet50_L10-20231006Oct26shuffle1_1230000", "led", "x")].to_numpy()
    y = df[("DLC_resnet50_L10-20231006Oct26shuffle1_1230000", "led", "y")].to_numpy()

    position = np.column_stack((x, y))
    pixels_to_cm = 5.3
    position_offset = 10

    position = position[position_offset:] / pixels_to_cm

    ref_time_offset = timestamps_ephys[predict_epoch][0]
    t_position = timestamps_position[predict_epoch][position_offset:] - ref_time_offset
    position_sampling_rate = len(t_position) / (t_position[-1] - t_position[0])
    start_time = t_position[0]
    end_time = t_position[-1]
    sampling_rate = int(1 / (2e-3))
    n_samples = int(np.ceil((end_time - start_time) * sampling_rate)) + 1

    time = np.linspace(start_time, end_time, n_samples)

    max_plausible_speed = (100.0,)
    position_smoothing_duration = 0.125
    speed_smoothing_std_dev = 0.100
    orient_smoothing_std_dev = 0.001
    # "led1_is_front": 1,
    # "is_upsampled": 0,
    # "upsampling_sampling_rate": None,
    upsampling_interpolation_method = "linear"

    speed = pt.get_speed(
        position,
        t_position,
        sigma=speed_smoothing_std_dev,
        sampling_frequency=position_sampling_rate,
    )

    is_too_fast = speed > max_plausible_speed
    position[is_too_fast] = np.nan

    position = pt.interpolate_nan(position)

    import bottleneck

    moving_average_window = int(position_smoothing_duration * position_sampling_rate)
    position = bottleneck.move_mean(
        position, window=moving_average_window, axis=0, min_count=1
    )

    def remove_tracking_errors(data, threshold=30):
        # Calculate the differences between consecutive points
        diffs = np.diff(data, axis=0)
        distances = np.linalg.norm(diffs, axis=1)

        # Identify points where the change exceeds the threshold
        error_indices = np.where(distances > threshold)[0] + 1

        # Handle edge case where the first or last point is an error
        if 0 in error_indices:
            data[0] = data[1]
        if len(data) - 1 in error_indices:
            data[-1] = data[-2]

        # Interpolate over errors
        for index in error_indices:
            if index < len(data) - 1:
                data[index] = (data[index - 1] + data[index + 1]) / 2

        return data

    def moving_average(data, window_size=3):
        """Simple moving average"""
        return np.convolve(data, np.ones(window_size) / window_size, mode="same")

    def remove_outliers_and_errors(data, jump_threshold=30, outlier_threshold=50):
        # Remove large jumps first
        data = remove_tracking_errors(data, threshold=jump_threshold)

        # Calculate smoothed trajectory
        smoothed_data = np.vstack(
            (moving_average(data[:, 0]), moving_average(data[:, 1]))
        ).T

        # Identify and handle outliers
        for i in range(len(data)):
            if np.linalg.norm(data[i] - smoothed_data[i]) > outlier_threshold:
                # Handle edge cases
                if i == 0:
                    data[i] = data[i + 1]
                elif i == len(data) - 1:
                    data[i] = data[i - 1]
                else:
                    data[i] = (data[i - 1] + data[i + 1]) / 2

        return data

    def detect_extended_jumps(data, smoothed_data, threshold):
        """Detects extended jumps in the data"""
        distances = np.linalg.norm(data - smoothed_data, axis=1)
        return distances > threshold

    def segment_data(data, is_jump):
        """Segments the data into normal and jump segments"""
        segments = []
        start = 0

        for i in range(1, len(is_jump)):
            if is_jump[i] != is_jump[i - 1]:
                segments.append((start, i, is_jump[i - 1]))
                start = i
        segments.append((start, len(is_jump), is_jump[-1]))

        return segments

    def interpolate_jumps(data, segments):
        """Interpolates over the segments identified as jumps"""
        for start, end, is_jump in segments:
            if is_jump:
                if start == 0:
                    data[start:end] = data[end]
                elif end == len(data):
                    data[start:end] = data[start - 1]
                else:
                    interp_values = np.linspace(data[start - 1], data[end], end - start)
                    data[start:end] = interp_values
        return data

    def remove_extended_jumps(
        data, jump_threshold=30, outlier_threshold=50, window_size=5
    ):
        # Initial jump removal
        data = remove_tracking_errors(data, threshold=jump_threshold)

        # Calculate smoothed trajectory
        smoothed_data = np.vstack(
            (
                moving_average(data[:, 0], window_size),
                moving_average(data[:, 1], window_size),
            )
        ).T

        # Detect extended jumps
        is_jump = detect_extended_jumps(data, smoothed_data, outlier_threshold)

        # Segment the data
        segments = segment_data(data, is_jump)

        # Interpolate over extended jumps
        return interpolate_jumps(data, segments)

    # Process the data
    position = remove_extended_jumps(position)

    # plt.plot(position[:,0], position[:,1])

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

    track_graph = tl.make_track_graph(node_positions, edges)

    position_df = tl.get_linearized_position(
        position=position,
        track_graph=track_graph,
        edge_order=linear_edge_order,
        edge_spacing=linear_edge_spacing,
    )

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
