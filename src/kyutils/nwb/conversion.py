from datetime import datetime
from uuid import uuid4

import numpy as np
from dateutil import tz
import spikeinterface.full as si
import probeinterface as pi

from pynwb import NWBHDF5IO, NWBFile
from pynwb.ecephys import ElectricalSeries
from pynwb.file import Subject

from ..probe.generate_probe import get_Livermore_20um, get_Livermore_15um
from .utils import (
    TimestampsExtractor,
    TimestampsDataChunkIterator,
    SpikeInterfaceRecordingDataChunkIterator,
)


def convert_to_nwb(
    dat_in_path: str, time_in_path: str, nwb_out_path: str, session_id: str = "1"
):
    """Minimal NWB conversion code for a four-probe (512 ch) implanted animal (e.g. L10) sampled at 20kHz.
    Assumes data has been exported to binary by trodesexport.
    Only converts ephys data and electrode information to NWB.

    Parameters
    ----------
    dat_in_path : str
        path to dat file containing recording
    time_in_path : str
        path to dat file containing time information
    nwb_out_path : str
        path to save the converted NWB file
    """
    # Create NWB file
    nwbfile = NWBFile(
        session_description="Homebox",
        identifier=str(uuid4()),
        session_start_time=datetime(
            2023, 9, 23, 19, 38, 35, tzinfo=tz.gettz("US/Pacific")
        ),
        experimenter=["Lee, Kyu Hyun", "Adenekan, Philip"],
        lab="Loren Frank",
        institution="University of California, San Francisco",
        experiment_description="L10 continuous recording in homebox",
        session_id="L10_1",
    )

    # Add subject info
    nwbfile.subject = Subject(
        subject_id="L10",
        description="Wildtype male Long Evans rat implanted with Livermore probes in the hippocampus CA1 and primary visual cortex on Aug 25, 2023.",
        species="Rattus norvegicus",
        sex="M",
        genotype="wt",
        weight="0.485 kg",
        date_of_birth=datetime(2023, 4, 24, tzinfo=tz.gettz("US/Pacific")),
        strain="Long Evans",
    )

    # Define probes
    device_left_v1 = nwbfile.create_device(
        name="Livermore left V1", description="128c-4s4mm-20um-sl", manufacturer="LLNL"
    )
    device_left_ca1 = nwbfile.create_device(
        name="Livermore left CA1", description="128c-4s6mm-15um-sl", manufacturer="LLNL"
    )
    device_right_ca1 = nwbfile.create_device(
        name="Livermore right CA1",
        description="128c-4s4mm-20um-sl",
        manufacturer="LLNL",
    )
    device_right_v1 = nwbfile.create_device(
        name="Livermore right V1", description="128c-4s6mm-15um-sl", manufacturer="LLNL"
    )

    devices = [device_left_v1, device_left_ca1, device_right_ca1, device_right_v1]

    probe_left_v1 = get_Livermore_20um(order=0)
    probe_left_ca1 = get_Livermore_15um(order=1, shift=[2000, 4000])
    probe_right_ca1 = get_Livermore_20um(order=2, shift=[6000, 4000])
    probe_right_v1 = get_Livermore_15um(order=3, shift=[8000, 0])

    probegroup = pi.ProbeGroup()
    probegroup.add_probe(probe_left_v1)
    probegroup.add_probe(probe_left_ca1)
    probegroup.add_probe(probe_right_ca1)
    probegroup.add_probe(probe_right_v1)

    # Set location
    locations = [
        "Cornu ammonis 1 (CA1)",
        "Primary visual area (V1)",
        "Primary visual area (V1)",
        "Cornu ammonis 1 (CA1)",
    ]

    # Add column to electrode table
    nwbfile.add_electrode_column(name="label", description="label of electrode")

    # Add electrodes
    for probe_idx, probe in enumerate(probegroup.probes):
        for shank_id in np.unique(probe.shank_ids):
            # create an electrode group for this shank
            electrode_group = nwbfile.create_electrode_group(
                name=f"probe {probe_idx} shank {shank_id}",
                description=f"electrode group for probe {probe_idx} shank {shank_id}",
                device=devices[probe_idx],
                location=locations[probe_idx],
            )
            for hwchan_id in probe.device_channel_indices[probe.shank_ids == shank_id]:
                nwbfile.add_electrode(
                    id=hwchan_id,
                    group=electrode_group,
                    label=f"probe {probe_idx} shank {shank_id} hwchan {hwchan_id}",
                    location=locations[probe_idx],
                    rel_x=probe.contact_positions[
                        probe.device_channel_indices == hwchan_id
                    ][0][0],
                    rel_y=probe.contact_positions[
                        probe.device_channel_indices == hwchan_id
                    ][0][1],
                    reference="skull screw",
                )

    # Define table region
    all_table_region = nwbfile.create_electrode_table_region(
        region=list(range(len(nwbfile.electrodes.id[:]))),
        description="all electrodes",
    )

    # Load recording
    recording = si.BinaryRecordingExtractor(
        file_paths=dat_in_path,
        sampling_frequency=20000,
        num_channels=512,
        dtype="int16",
        gain_to_uV=0.19500000000000001,
        offset_to_uV=0,
        is_filtered=False,
    )

    # Match channel order to electrode table
    recording = recording.channel_slice(channel_ids=nwbfile.electrodes.id[:])

    data_iterator = SpikeInterfaceRecordingDataChunkIterator(
        recording=recording, return_scaled=False, buffer_gb=3
    )

    # Load timestamps
    timestamps_extractor = TimestampsExtractor(time_in_path, sampling_frequency=20e3)

    timestamps_iterator = TimestampsDataChunkIterator(
        recording=timestamps_extractor, buffer_gb=3
    )

    raw_electrical_series = ElectricalSeries(
        name="ElectricalSeries",
        data=data_iterator,
        electrodes=all_table_region,
        timestamps=timestamps_iterator,
        conversion=0.19500000000000001e-6,
        offset=0.0,
    )

    nwbfile.add_acquisition(raw_electrical_series)

    with NWBHDF5IO(nwb_out_path, "w") as io:
        io.write(nwbfile)
