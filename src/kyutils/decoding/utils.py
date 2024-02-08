import numpy as np
import bottleneck
import position_tools as pt


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
