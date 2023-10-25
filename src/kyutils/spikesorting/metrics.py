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

    isi_violation_fraction_params = {"isi_threshold_ms": 2.0, "min_isi_ms": 0}

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
        _, count = sq.compute_isi_violations(
            waveform_extractor, unit_ids=[i], **isi_violation_fraction_params
        )
        isi_violation_fraction[i] = count / (
            len(waveform_extractor.sorting.get_unit_spike_train(i)) - 1
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
