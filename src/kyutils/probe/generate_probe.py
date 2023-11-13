from typing import List, Union
import numpy as np
import probeinterface as pi


def get_Livermore_15um(
    device_channel_indices: Union[str, List] = "SpikeGadgets",
    order: int = 0,
    shift=[0, 0],
):
    """Returns a probeinterface Probe object of the Livermore 15um probe.

    Parameters
    ----------
    device_channel_indices : str or iterable
        The mapping from the contact IDs to device channel indices;
        depends on the hardware, by default assumes SpikeGadgets H70 probe board
    order : int
        order in a probegroup, by default 0
    shift : list, optional
        how much to shift the channel locations by, by default [0,0] (important for probegroup)
    """
    Livermore_15um = pi.generate_multi_shank(
        num_shank=4,
        shank_pitch=[250, 0],
        num_columns=1,
        num_contact_per_column=32,
        xpitch=0,
        ypitch=26,
        y_shift_per_column=None,
        contact_shapes="circle",
        contact_shape_params={"radius": 15 / 2},
    )

    # flip because electrodes should be facing you
    contact_ids = np.concatenate(
        [np.arange(96, 128), np.arange(64, 96), np.arange(32, 64), np.arange(0, 32)]
    )
    contact_ids = contact_ids + order * 128
    Livermore_15um.set_contact_ids(contact_ids)
    if device_channel_indices == "SpikeGadgets":
        device_channel_indices = np.array(
            [
                35,
                39,
                43,
                47,
                50,
                54,
                58,
                62,
                4,
                0,
                5,
                32,
                12,
                20,
                17,
                8,
                34,
                38,
                42,
                46,
                51,
                55,
                59,
                63,
                24,
                16,
                13,
                9,
                21,
                28,
                25,
                29,
                33,
                37,
                41,
                45,
                48,
                52,
                56,
                61,
                18,
                22,
                26,
                30,
                3,
                1,
                7,
                15,
                31,
                36,
                40,
                44,
                49,
                53,
                57,
                60,
                11,
                2,
                6,
                10,
                14,
                19,
                23,
                27,
                124,
                126,
                120,
                112,
                109,
                105,
                101,
                97,
                79,
                75,
                71,
                66,
                94,
                90,
                86,
                82,
                116,
                125,
                121,
                117,
                113,
                108,
                104,
                100,
                95,
                91,
                87,
                83,
                78,
                74,
                70,
                67,
                115,
                107,
                110,
                119,
                123,
                127,
                122,
                96,
                77,
                73,
                69,
                65,
                92,
                88,
                84,
                80,
                103,
                111,
                114,
                118,
                106,
                99,
                102,
                98,
                93,
                89,
                85,
                81,
                76,
                72,
                68,
                64,
            ]
        )
    device_channel_indices = device_channel_indices + order * 128
    Livermore_15um.set_device_channel_indices(device_channel_indices)
    Livermore_15um.move(shift)
    return Livermore_15um


def get_Livermore_20um(
    device_channel_indices: Union[str, List] = "SpikeGadgets",
    order: int = 0,
    shift=[0, 0],
):
    """Returns a probeinterface Probe object of the Livermore 20um probe

    Parameters
    ----------
    device_channel_indices : str or iterable
        The mapping from the contact IDs to device channel indices;
        depends on the hardware, by default assumes SpikeGadgets H70 probe board
    order : int
        order in a probegroup, by default 0
    shift : list, optional
        how much to shift the channel locations by, by default [0,0] (important for probegroup)
    """
    Livermore_20um = pi.generate_multi_shank(
        num_shank=4,
        shank_pitch=[250, 0],
        num_columns=1,
        num_contact_per_column=32,
        xpitch=0,
        ypitch=40,
        y_shift_per_column=None,
        contact_shapes="circle",
        contact_shape_params={"radius": 10},
    )

    # flip because electrodes should be facing you
    contact_ids = np.concatenate(
        [np.arange(96, 128), np.arange(64, 96), np.arange(32, 64), np.arange(0, 32)]
    )
    contact_ids = contact_ids + order * 128
    Livermore_20um.set_contact_ids(contact_ids)
    if device_channel_indices == "SpikeGadgets":
        device_channel_indices = np.array(
            [
                35,
                39,
                43,
                47,
                50,
                54,
                58,
                62,
                4,
                0,
                5,
                32,
                12,
                20,
                17,
                8,
                34,
                38,
                42,
                46,
                51,
                55,
                59,
                63,
                21,
                28,
                25,
                29,
                24,
                16,
                13,
                9,
                33,
                37,
                41,
                45,
                48,
                52,
                56,
                61,
                18,
                22,
                26,
                30,
                3,
                1,
                7,
                15,
                31,
                36,
                40,
                44,
                49,
                53,
                57,
                60,
                14,
                19,
                23,
                27,
                11,
                2,
                6,
                10,
                124,
                126,
                120,
                112,
                109,
                105,
                101,
                97,
                79,
                75,
                71,
                66,
                94,
                90,
                86,
                82,
                116,
                125,
                121,
                117,
                113,
                108,
                104,
                100,
                78,
                74,
                70,
                67,
                95,
                91,
                87,
                83,
                115,
                107,
                110,
                119,
                123,
                127,
                122,
                96,
                77,
                73,
                69,
                65,
                92,
                88,
                84,
                80,
                103,
                111,
                114,
                118,
                106,
                99,
                102,
                98,
                76,
                72,
                68,
                64,
                93,
                89,
                85,
                81,
            ]
        )
    device_channel_indices = device_channel_indices + order * 128
    Livermore_20um.set_device_channel_indices(device_channel_indices)
    Livermore_20um.move(shift)
    return Livermore_20um
