import spikeinterface.full as si
import json
import numpy as np

def compute_standard_metrics(waveform_extractor, path_to_json):

    snrs = si.compute_snrs(waveform_extractor, random_chunk_kwargs_dict= {
                    "num_chunks_per_segment": 20,
                    "chunk_size": 10000,
                    "seed": 0,
                },)

    _, isi_violation_count = si.compute_isi_violations(waveform_extractor, isi_threshold_ms=2)

    nn_isolation_params = {
                "max_spikes": 1000,
                "min_spikes": 10,
                "n_neighbors": 5,
                "n_components": 7,
                "radius_um": 100,
                "seed": 0,
            }
    nn_isolation = {}
    for i in waveform_extractor.sorting.get_unit_ids():
        nn_isolation[i] = si.nearest_neighbors_isolation(waveform_extractor, this_unit_id=i,**nn_isolation_params)
    
    nn_noise_params = {
            "max_spikes": 1000,
            "min_spikes": 10,
            "n_neighbors": 5,
            "n_components": 7,
            "radius_um": 100,
            "seed": 0,
        }
    nn_noise = {}
    for i in waveform_extractor.sorting.get_unit_ids():
        nn_noise[i] = si.nearest_neighbors_noise_overlap(waveform_extractor, this_unit_id=i,**nn_noise_params)

    metrics_dict={}

    metrics_dict['snr'] = snrs
    metrics_dict['isi_violation_count'] = isi_violation_count
    metrics_dict['nn_isolation'] = nn_isolation
    metrics_dict['nn_noise_overlap'] = nn_noise

    for metric_name, metric_data in metrics_dict.items():
        metrics_dict[metric_name] = {str(i): np.float64(j) for i,j in metric_data.items()}

    with open(path_to_json, 'w') as f:
        # Serialize the dictionary and write it to the file
        json.dump(metrics_dict, f)
        
    return metrics_dict