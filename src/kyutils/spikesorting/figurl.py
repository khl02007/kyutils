def create_figurl_spikesorting(
    recording, sorting, label: str, curation_uri: str = None
):
    """Creates a figurl to view the sorting results.

    Parameters
    ----------
    recording : si.Recording
        Recording; have to be either Binary or NWB recording
    sorting : si.Sorting
        Sorting; have to be NpzSortingExtractor
    label : str
        label for this figurl
    curation_uri : str, optional
        path to json file containing curation information in the GitHub repository, by default None
        example: "gh://LorenFrankLab/sorting-curations/main/khl02007/L5/20230411_r3_20230511_r1/curation.json"

    Returns
    -------
    url : str
        figurl
    """
    try:
        import kachery_cloud as kcl
        import sortingview as sv
        import sortingview.views as vv
        from sortingview.SpikeSortingView import SpikeSortingView
    except ImportError as e:
        print(
            f"Error: {e}. Please install `kachery-cloud` and `sortingview` to proceed."
        )
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
    if curation_uri:
        url_state = {"sortingCuration": curation_uri}
    else:
        url_state = None
    url = view.url(label=label, state=url_state)
    return url
