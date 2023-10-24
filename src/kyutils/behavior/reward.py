import numpy as np
from ..spikegadgets.trodesconf import readTrodesExtractedDataFile


def get_licks_rewards(time, Din_well, Dout_pump):
    """Returns the (relative) timing of the following events:
    - every lick at a reward well
    - the first lick of a train of licks (typically when the animal licks it licks many times)
    - pump turning on to deliver milk reward
    - the lick that was followed by reward

    Parameters
    ----------
    time : dict
        output of readTrodesExtractedDataFile for time
    Din_well : dict
        output of readTrodesExtractedDataFile for DIO
    Dout_pump : dict
        output of readTrodesExtractedDataFile for DIO

    Returns
    -------
    lick_times
    first_lick_times
    pump_on_times
    rewarded_lick_times:
        _description_
    """
    x = []
    for i in Din_well["data"]["time"]:
        x.append(time["data"]["systime"][np.nonzero(time["data"]["time"] == i)[0][0]])
    x = np.asarray(x)
    x = (x - time["data"]["systime"][0]) * 1e-9

    lick_times = [x[i] for i in range(len(x)) if Din_well["data"]["state"][i] == 1]
    lick_times = np.asarray(lick_times)

    # time between lick trains (unit: seconds)
    lick_train_interval_s = 13

    first_lick_times = lick_times[
        np.nonzero(np.diff(lick_times) > lick_train_interval_s)[0] + 1
    ]
    first_lick_times = np.insert(first_lick_times, 0, lick_times[0])

    pump_times = []
    for i in Dout_pump["data"]["time"]:
        pump_times.append(
            time["data"]["systime"][np.nonzero(time["data"]["time"] == i)[0][0]]
        )
    pump_times = np.asarray(pump_times)
    pump_times = (pump_times - time["data"]["systime"][0]) * 1e-9

    pump_on_times = [
        pump_times[i]
        for i in range(len(pump_times))
        if Dout_pump["data"]["state"][i] == 1
    ]

    # delay between detection of lick and delivery of reward (unit: seconds)
    rewarded_lick_times = [
        i
        for i in first_lick_times
        if np.min(np.abs(pump_on_times - i)) < rewarded_lick_times
    ]

    return lick_times, first_lick_times, pump_on_times, rewarded_lick_times


def plot_performance(
    ax,
    first_lick_times_left,
    first_lick_times_center,
    first_lick_times_right,
    rewarded_lick_times_left,
    rewarded_lick_times_center,
    rewarded_lick_times_right,
    pump_on_times_left,
    pump_on_times_center,
    pump_on_times_right,
):
    ax.plot(
        first_lick_times_left,
        np.ones(len(first_lick_times_left)),
        "bo",
        markersize=10,
        markerfacecolor="none",
    )
    ax.plot(
        rewarded_lick_times_left,
        np.ones(len(rewarded_lick_times_left)),
        "bo",
        markersize=10,
    )

    ax.plot(
        first_lick_times_center,
        2 * np.ones(len(first_lick_times_center)),
        "ro",
        markersize=10,
        markerfacecolor="none",
    )
    ax.plot(
        rewarded_lick_times_center,
        2 * np.ones(len(rewarded_lick_times_center)),
        "ro",
        markersize=10,
    )

    ax.plot(
        first_lick_times_right,
        3 * np.ones(len(first_lick_times_right)),
        "go",
        markersize=10,
        markerfacecolor="none",
    )
    ax.plot(
        rewarded_lick_times_right,
        3 * np.ones(len(rewarded_lick_times_right)),
        "go",
        markersize=10,
    )

    ax.set_xlabel("Time (s)")
    ax.set_ylim([0, 4])

    ticks = [1, 2, 3]  # Replace with your desired tick locations
    ax.set_yticks(ticks)

    # Define the new tick labels
    labels = ["Left", "Center", "Right"]  # Replace with your custom labels

    # Set the new tick labels
    ax.set_yticklabels(labels)
    performance = (
        len(pump_on_times_left) + len(pump_on_times_center) + len(pump_on_times_right)
    ) / (
        len(first_lick_times_left)
        + len(first_lick_times_center)
        + len(first_lick_times_right)
    )
    ax.set_title(f"Overall performance: {performance}")
