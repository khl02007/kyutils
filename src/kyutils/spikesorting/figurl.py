from typing import List


# curation_uri = "gh://LorenFrankLab/sorting-curations/main/khl02007/L5/20230411_r3_20230511_r1/curation.json"
def create_figurl_spikesorting(recording, sorting, curation_uri, label):
    try:
        import kachery_cloud as kcl
        import sortingview as sv
        import sortingview.views as vv
        from sortingview.SpikeSortingView import SpikeSortingView
    except ImportError as e:
        print(f"Error: {e}. Please install the missing package to proceed.")
        return  # exit the function or handle this as needed

    X = SpikeSortingView.create(
        recording=recording,
        sorting=sorting,
        segment_duration_sec=60 * 20,
        snippet_len=(20, 20),
        max_num_snippets_per_segment=300,
        channel_neighborhood_size=12,
    )

    # Assemble the views in a layout
    # You can replace this with other layouts
    raster_plot_subsample_max_firing_rate = 50
    spike_amplitudes_subsample_max_firing_rate = 50
    view = vv.MountainLayout(
        items=[
            vv.MountainLayoutItem(label="Summary", view=X.sorting_summary_view()),
            vv.MountainLayoutItem(
                label="Units table",
                view=X.units_table_view(unit_ids=X.unit_ids),
            ),
            vv.MountainLayoutItem(
                label="Raster plot",
                view=X.raster_plot_view(
                    unit_ids=X.unit_ids,
                    _subsample_max_firing_rate=raster_plot_subsample_max_firing_rate,
                ),
            ),
            vv.MountainLayoutItem(
                label="Spike amplitudes",
                view=X.spike_amplitudes_view(
                    unit_ids=X.unit_ids,
                    _subsample_max_firing_rate=spike_amplitudes_subsample_max_firing_rate,
                ),
            ),
            vv.MountainLayoutItem(
                label="Autocorrelograms",
                view=X.autocorrelograms_view(unit_ids=X.unit_ids),
            ),
            vv.MountainLayoutItem(
                label="Cross correlograms",
                view=X.cross_correlograms_view(unit_ids=X.unit_ids),
            ),
            vv.MountainLayoutItem(
                label="Avg waveforms",
                view=X.average_waveforms_view(unit_ids=X.unit_ids),
            ),
            vv.MountainLayoutItem(
                label="Electrode geometry", view=X.electrode_geometry_view()
            ),
            vv.MountainLayoutItem(
                label="Curation", view=vv.SortingCuration2(), is_control=True
            ),
        ]
    )
    url_state = {"sortingCuration": curation_uri}
    url = view.url(label=label, state=url_state)
    return url
