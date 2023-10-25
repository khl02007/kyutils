import spikeinterface as si
import spikeinterface.qualitymetrics as sq

import json
import numpy as np


def compute_standard_metrics(waveform_extractor, path_to_json):
    snrs = sq.compute_snrs(
        waveform_extractor,
        random_chunk_kwargs_dict={
            "num_chunks_per_segment": 20,
            "chunk_size": 10000,
            "seed": 0,
        },
    )

    nn_isolation_params = {
        "max_spikes": 1000,
        "min_spikes": 10,
        "n_neighbors": 5,
        "n_components": 7,
        "radius_um": 200,
        "seed": 0,
    }
    nn_noise_params = {
        "max_spikes": 1000,
        "min_spikes": 10,
        "n_neighbors": 5,
        "n_components": 7,
        "radius_um": 200,
        "seed": 0,
    }

    isi_violation_fraction = {}
    nn_isolation = {}
    nn_noise = {}
    for i in waveform_extractor.sorting.get_unit_ids():
        isi_violation_fraction[i] = compute_isi_violation_fractions(
            waveform_extractor, this_unit_id=i
        )
        nn_isolation[i] = sq.nearest_neighbors_isolation(
            waveform_extractor, this_unit_id=i, **nn_isolation_params
        )
        nn_noise[i] = sq.nearest_neighbors_noise_overlap(
            waveform_extractor, this_unit_id=i, **nn_noise_params
        )

    metrics_dict = {}

    metrics_dict["snr"] = snrs
    metrics_dict["isi_violation_fraction"] = isi_violation_fraction
    metrics_dict["nn_isolation"] = nn_isolation
    metrics_dict["nn_noise_overlap"] = nn_noise

    for metric_name, metric_data in metrics_dict.items():
        metrics_dict[metric_name] = {
            str(i): np.float64(j) for i, j in metric_data.items()
        }

    with open(path_to_json, "w") as f:
        # Serialize the dictionary and write it to the file
        json.dump(metrics_dict, f)

    return metrics_dict


def compute_isi_violation_fractions(
    waveform_extractor: si.WaveformExtractor,
    this_unit_id: str,
    isi_threshold_ms: float = 2.0,
    min_isi_ms: float = 0.0,
):
    """Computes the fraction of interspike interval violations.

    Parameters
    ----------
    waveform_extractor: si.WaveformExtractor
        The extractor object for the recording.

    """

    # Extract the total number of spikes that violated the isi_threshold for each unit
    isi_violation_counts = np.asarray(
        sq.compute_isi_violations(
            waveform_extractor,
            isi_threshold_ms=isi_threshold_ms,
            min_isi_ms=min_isi_ms,
        ).isi_violations_count
    )

    isi_violation_count = isi_violation_counts[
        waveform_extractor.sorting.get_unit_ids() == this_unit_id
    ]
    total_spike_count = get_num_spikes(waveform_extractor, this_unit_id)
    return isi_violation_count / (total_spike_count - 1)


def get_peak_offset(
    waveform_extractor: si.WaveformExtractor, peak_sign: str, **metric_params
):
    """Computes the shift of the waveform peak from center of window.

    Parameters
    ----------
    waveform_extractor: si.WaveformExtractor
        The extractor object for the recording.
    peak_sign: str
        The sign of the peak to compute. ('neg', 'pos', 'both')
    """
    if "peak_sign" in metric_params:
        del metric_params["peak_sign"]
    peak_offset_inds = si.get_template_extremum_channel_peak_shift(
        waveform_extractor=waveform_extractor,
        peak_sign=peak_sign,
        **metric_params,
    )
    peak_offset = {key: int(abs(val)) for key, val in peak_offset_inds.items()}
    return peak_offset


def get_peak_channel(
    waveform_extractor: si.WaveformExtractor, peak_sign: str, **metric_params
):
    """Computes the electrode_id of the channel with the extremum peak for each unit."""
    if "peak_sign" in metric_params:
        del metric_params["peak_sign"]
    peak_channel_dict = si.get_template_extremum_channel(
        waveform_extractor=waveform_extractor,
        peak_sign=peak_sign,
        **metric_params,
    )
    peak_channel = {key: int(val) for key, val in peak_channel_dict.items()}
    return peak_channel


def get_num_spikes(waveform_extractor: si.WaveformExtractor, this_unit_id: str):
    """Computes the number of spikes for each unit."""
    all_spikes = sq.compute_num_spikes(waveform_extractor)
    unit_spikes = all_spikes[waveform_extractor.sorting.get_unit_ids() == this_unit_id]
    return unit_spikes
