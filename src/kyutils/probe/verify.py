import spikeinterface.full as si
import probeinterface as pi
import numpy as np
import kyutils
import matplotlib.pyplot as plt

dat_path = "/cumulus/kyu/L10/20231006/s1/20231006_144958/20231006_144958.kilosort/20231006_144958.group0.dat"
# dat_path = '/cumulus/kyu/L10/20231006/s3/20231006_170918/20231006_170918.kilosort/20231006_170918.group0.dat'
# '/nimbus/kyu/army/20240207/r1/20240207_152943/20240207_army_01_r1.kilosort/20240207_army_01_r1.group0.dat'
nwb_path = "/stelmo/kyu/L1020231006.nwb"


def get_recording():
    path_to_data = "/cumulus/kyu/L10/20231006/"

    s1_path = (
        path_to_data
        + "s1/20231006_144958/20231006_144958.kilosort/20231006_144958.group0.dat"
    )
    r1_path = (
        path_to_data
        + "r1/20231006_154913/20231006_154913.kilosort/20231006_154913.group0.dat"
    )
    s2_path = (
        path_to_data
        + "s2/20231006_161321/20231006_161321.kilosort/20231006_161321.group0.dat"
    )
    r2_path = (
        path_to_data
        + "r2/20231006_164457/20231006_164457.kilosort/20231006_164457.group0.dat"
    )
    s3_path = (
        path_to_data
        + "s3/20231006_170918/20231006_170918.kilosort/20231006_170918.group0.dat"
    )
    r3_path = (
        path_to_data
        + "r3/20231006_173707/20231006_173707.kilosort/20231006_173707.group0.dat"
    )
    s4_path = (
        path_to_data
        + "s4/20231006_180140/20231006_180140.kilosort/20231006_180140.group0.dat"
    )

    recording_s1 = si.BinaryRecordingExtractor(
        s1_path,
        sampling_frequency=30e3,
        dtype=np.int16,
        num_channels=512,
        gain_to_uV=0.19500000000000001,
        offset_to_uV=0,
        is_filtered=False,
    )

    recording_r1 = si.BinaryRecordingExtractor(
        r1_path,
        sampling_frequency=30e3,
        dtype=np.int16,
        num_channels=512,
        gain_to_uV=0.19500000000000001,
        offset_to_uV=0,
        is_filtered=False,
    )

    recording_s2 = si.BinaryRecordingExtractor(
        s2_path,
        sampling_frequency=30e3,
        dtype=np.int16,
        num_channels=512,
        gain_to_uV=0.19500000000000001,
        offset_to_uV=0,
        is_filtered=False,
    )

    recording_r2 = si.BinaryRecordingExtractor(
        r2_path,
        sampling_frequency=30e3,
        dtype=np.int16,
        num_channels=512,
        gain_to_uV=0.19500000000000001,
        offset_to_uV=0,
        is_filtered=False,
    )

    recording_s3 = si.BinaryRecordingExtractor(
        s3_path,
        sampling_frequency=30e3,
        dtype=np.int16,
        num_channels=512,
        gain_to_uV=0.19500000000000001,
        offset_to_uV=0,
        is_filtered=False,
    )

    recording_r3 = si.BinaryRecordingExtractor(
        r3_path,
        sampling_frequency=30e3,
        dtype=np.int16,
        num_channels=512,
        gain_to_uV=0.19500000000000001,
        offset_to_uV=0,
        is_filtered=False,
    )

    recording_s4 = si.BinaryRecordingExtractor(
        s4_path,
        sampling_frequency=30e3,
        dtype=np.int16,
        num_channels=512,
        gain_to_uV=0.19500000000000001,
        offset_to_uV=0,
        is_filtered=False,
    )
    recording = si.concatenate_recordings(
        [
            recording_s1,
            recording_r1,
            recording_s2,
            recording_r2,
            recording_s3,
            recording_r3,
            recording_s4,
        ]
    )

    probe_left_v1 = kyutils.get_Livermore_20um(order=0)
    probe_left_ca1 = kyutils.get_Livermore_15um(order=1, shift=[2000, 4000])
    probe_right_ca1 = kyutils.get_Livermore_20um(order=2, shift=[6000, 4000])
    probe_right_v1 = kyutils.get_Livermore_15um(order=3, shift=[8000, 0])

    probegroup = pi.ProbeGroup()
    probegroup.add_probe(probe_left_v1)
    probegroup.add_probe(probe_left_ca1)
    probegroup.add_probe(probe_right_ca1)
    probegroup.add_probe(probe_right_v1)

    recording = recording.set_probegroup(probegroup)
    return recording


def compare_binary_to_nwb(
    dat_path, nwb_path, target_channel_id=3, frames_to_compare=3000
):

    recording_dat = si.BinaryRecordingExtractor(
        dat_path,
        sampling_frequency=30e3,
        dtype=np.int16,
        num_channels=512,
        gain_to_uV=0.19500000000000001,
        offset_to_uV=0,
        is_filtered=False,
    )

    probe_left_v1 = kyutils.get_Livermore_20um(order=0)
    probe_left_ca1 = kyutils.get_Livermore_15um(order=1, shift=[2000, 4000])
    probe_right_ca1 = kyutils.get_Livermore_20um(order=2, shift=[6000, 4000])
    probe_right_v1 = kyutils.get_Livermore_15um(order=3, shift=[8000, 0])

    probegroup = pi.ProbeGroup()
    probegroup.add_probe(probe_left_v1)
    probegroup.add_probe(probe_left_ca1)
    probegroup.add_probe(probe_right_ca1)
    probegroup.add_probe(probe_right_v1)

    recording_dat = recording_dat.set_probegroup(probegroup)
    recording_nwb = si.read_nwb_recording(nwb_path)

    if type(target_channel_id) is int:
        target_channel_id = [target_channel_id]
    print(
        f"Using channel {target_channel_id} from binary recording to compare with NWB recording."
    )

    target_channel_loc = recording_dat.get_channel_locations()[
        recording_dat.get_channel_ids() == target_channel_id
    ]
    print(
        f"Location of channel {target_channel_id} from binary recording: {target_channel_loc}"
    )

    # target_channel_idx_dat = np.where(np.all(recording_dat.get_channel_locations() == target_channel_loc, axis=1))[0]
    target_channel_idx_nwb = np.where(
        np.all(recording_nwb.get_channel_locations() == target_channel_loc, axis=1)
    )[0]
    target_channel_id_nwb = recording_nwb.get_channel_ids()[target_channel_idx_nwb]
    target_channel_loc_nwb = recording_nwb.get_channel_locations()[
        target_channel_idx_nwb
    ]

    print(
        f"Channel {target_channel_id} in binary recording is channel {target_channel_id_nwb} in NWB recording."
    )
    print(
        f"Location of channel {target_channel_id_nwb} in NWB recording: {target_channel_loc_nwb}"
    )

    traces_dat = recording_dat.get_traces(
        end_frame=frames_to_compare, channel_ids=target_channel_id, return_scaled=True
    )
    traces_nwb = recording_nwb.get_traces(
        end_frame=frames_to_compare,
        channel_ids=target_channel_id_nwb,
        return_scaled=True,
    )

    plt.plot(traces_dat, label="binary")
    plt.plot(traces_nwb, label="nwb")
    plt.legend()
    plt.ylabel("Voltage ($\mu$V)")
    plt.xlabel("Time from first sample (samples)")

    print(
        f"Do the values agree to within 1 microV? {np.allclose(traces_dat, traces_nwb, atol=1)}"
    )


def compare_binary_to_nwb2(
    nwb_path, target_channel_id=3, start_frame=3000, end_frame=30000
):

    recording_dat = get_recording()
    recording_nwb = si.read_nwb_recording(nwb_path)

    if type(target_channel_id) is int:
        target_channel_id = [target_channel_id]
    print(
        f"Using channel {target_channel_id} from binary recording to compare with NWB recording."
    )

    target_channel_loc = recording_dat.get_channel_locations()[
        recording_dat.get_channel_ids() == target_channel_id
    ]
    print(
        f"Location of channel {target_channel_id} from binary recording: {target_channel_loc}"
    )

    # target_channel_idx_dat = np.where(np.all(recording_dat.get_channel_locations() == target_channel_loc, axis=1))[0]
    target_channel_idx_nwb = np.where(
        np.all(recording_nwb.get_channel_locations() == target_channel_loc, axis=1)
    )[0]
    target_channel_id_nwb = recording_nwb.get_channel_ids()[target_channel_idx_nwb]
    target_channel_loc_nwb = recording_nwb.get_channel_locations()[
        target_channel_idx_nwb
    ]

    print(
        f"Channel {target_channel_id} in binary recording is channel {target_channel_id_nwb} in NWB recording."
    )
    print(
        f"Location of channel {target_channel_id_nwb} in NWB recording: {target_channel_loc_nwb}"
    )

    traces_dat = recording_dat.get_traces(
        start_frame=start_frame,
        end_frame=end_frame,
        channel_ids=target_channel_id,
        return_scaled=True,
    )
    traces_nwb = recording_nwb.get_traces(
        start_frame=start_frame,
        end_frame=end_frame,
        channel_ids=target_channel_id_nwb,
        return_scaled=True,
    )
    t = np.arange(start_frame, end_frame)

    fig, ax = plt.subplots()
    ax.plot(t, traces_dat, label="binary")
    ax.plot(t, traces_nwb, label="nwb")
    ax.legend()
    ax.set_ylabel("Voltage ($\mu$V)")
    ax.set_xlabel("Time (samples)")

    print(
        f"Do the values agree to within 1 microV? {np.allclose(traces_dat, traces_nwb, atol=1)}"
    )


# compare_binary_to_nwb2(
#     nwb_path, target_channel_id=300, start_frame=300000, end_frame=304000
# )
