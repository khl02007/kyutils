import numpy as np
import bottleneck
import position_tools as pt
import trajectory_analysis_tools as tat


def get_spike_indicator(sorting, time, timestamps_ephys):
    """_summary_

    Parameters
    ----------
    sorting : _type_
        _description_
    time : _type_
        time vector for decoding
    timestamps_ephys : _type_
        timestamps for ephys

    Returns
    -------
    _type_
        _description_
    """
    spike_indicator = []
    for unit_id in sorting.get_unit_ids():
        spike_times = timestamps_ephys[sorting.get_unit_spike_train(unit_id)]
        spike_times = spike_times[(spike_times > time[0]) & (spike_times <= time[-1])]
        spike_indicator.append(
            np.bincount(np.digitize(spike_times, time[1:-1]), minlength=time.shape[0])
        )
    return np.asarray(spike_indicator).T


def smooth_position(position, t_position, position_sampling_rate):
    # "max_LED_separation": 9.0,
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

    moving_average_window = int(position_smoothing_duration * position_sampling_rate)
    position = bottleneck.move_mean(
        position, window=moving_average_window, axis=0, min_count=1
    )
    return position


def get_ahead_behind(
    decode_acausal_posterior_1d,
    track_graph,
    classifier_1d,
    position_2d,
    track_segment_id,
    head_direction,
):
    (
        actual_projected_position,
        actual_edges,
        actual_orientation,
        mental_position_2d,
        mental_position_edges,
    ) = tat.get_trajectory_data(
        posterior=decode_acausal_posterior_1d,
        track_graph=track_graph,
        decoder=classifier_1d,
        actual_projected_position=position_2d,
        track_segment_id=track_segment_id,
        actual_orientation=head_direction,
    )
    return tat.get_ahead_behind_distance(
        track_graph,
        actual_projected_position,
        actual_edges,
        actual_orientation,
        mental_position_2d,
        mental_position_edges,
    )


from scipy.signal import correlate


def plot_linearized_position(
    ax, start_time, end_time, first=False, last=False, filter_freq=30
):
    idx = (time > start_time) & (time < end_time)

    ax.plot(time[idx], position_df["linear_position"][idx], "k", linewidth=3, alpha=0.5)
    # ax.plot(time[idx], map_decode_hpc_filtered[idx], 'r--')
    # ax.plot(time[idx], map_decode_v1_filtered[idx], 'b--')

    ahead_behind_distance_hpc_filtered = lowpass_filter(
        ahead_behind_distance_hpc, filter_freq, 500
    )
    ahead_behind_distance_v1_filtered = lowpass_filter(
        ahead_behind_distance_v1, filter_freq, 500
    )

    ax.plot(
        time[idx],
        position_df["linear_position"][idx] + ahead_behind_distance_hpc_filtered[idx],
        "b",
        linewidth=1,
        alpha=1,
    )
    ax.plot(
        time[idx],
        position_df["linear_position"][idx] + ahead_behind_distance_v1_filtered[idx],
        "r",
        linewidth=1,
        alpha=1,
    )

    if first:
        ax.set_ylabel("Linearized position")

    if last:
        ax.text(
            time[idx][0] + 0.4,
            20,
            "Actual",
            ha="center",
            va="center",
            color="k",
            fontsize=12,
            alpha=0.5,
        )

        ax.plot([time[idx][0] + 0.1, time[idx][0] + 0.1], [50, 100], "k")
        ax.text(
            time[idx][0] + 0.4,
            75,
            "50 cm",
            ha="center",
            va="center",
            color="k",
            fontsize=9,
        )
    ax.set_xlim([start_time, end_time])
    ax.set_ylim([0, 360])
    ax.set_xticks([])
    ax.set_yticks([])


def plot_deviation(ax, start_time, end_time, first=False, last=False, filter_freq=6):
    idx = (time > start_time) & (time < end_time)

    ahead_behind_distance_hpc_filtered = lowpass_filter(
        ahead_behind_distance_hpc, filter_freq, 500
    )
    ahead_behind_distance_v1_filtered = lowpass_filter(
        ahead_behind_distance_v1, filter_freq, 500
    )

    ax.axhline(0, color="k", alpha=0.5)
    ax.plot(time[idx], ahead_behind_distance_hpc_filtered[idx], "b")
    ax.plot(time[idx], ahead_behind_distance_v1_filtered[idx], "r")
    ax.plot(
        [time[idx][-1] - 0.5 - 0.5, time[idx][-1] - 0.5],
        [-20, -20],
        "k",
    )
    if last:
        ax.text(
            time[idx][-1] - 0.5 - 0.25,
            -23,
            "500 ms",
            ha="center",
            va="center",
            color="k",
            fontsize=9,
        )
        ax.plot([time[idx][-1] - 0.5, time[idx][-1] - 0.5], [-20, -10], "k")
        ax.text(
            time[idx][-1] - 0.25,
            -15,
            "10 cm",
            ha="center",
            va="center",
            color="k",
            fontsize=9,
        )
        ax.text(
            time[idx][0] + 0.5,
            -20,
            "HPC",
            ha="right",
            va="center",
            color="b",
            fontsize=12,
        )
        ax.text(
            time[idx][0] + 0.8,
            -20,
            "V1",
            ha="right",
            va="center",
            color="r",
            fontsize=12,
        )
    if first:
        ax.set_ylabel("Deviation")
    # ax.set_ylabel("Decoded-actual (cm)")
    ax.set_ylim([-25, 25])
    ax.set_xlim([start_time, end_time])
    ax.set_xticks([])
    ax.set_yticks([])


# idx = (time > int(min*60+sec)) & (time < int(min*60+sec+dt))


# plot_linearized_position(ax[0,0], 702.65, 705)
# plot_deviation(ax[1,0], 702.65, 705)


def lowpass_filter(data, cutoff, fs, order=5):
    """
    Apply a Butterworth lowpass filter to a NumPy array.

    :param data: NumPy array containing the data to filter.
    :param cutoff: Cut-off frequency of the filter.
    :param fs: Sampling rate of the data.
    :param order: Order of the filter.
    :return: Filtered data.
    """
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype="low", analog=False)
    y = filtfilt(b, a, data)
    return y
