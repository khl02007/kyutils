from typing import List, Tuple, Iterable, Optional, Union

from datetime import datetime, timedelta, timezone
import pytz

import numpy as np

from hdmf.data_utils import GenericDataChunkIterator
from spikeinterface.core import BaseRecording, BaseRecordingSegment
from ..spikegadgets.trodesconf import readTrodesExtractedDataFile


class SpikeInterfaceRecordingDataChunkIterator(GenericDataChunkIterator):
    """DataChunkIterator specifically for use on RecordingExtractor objects."""

    def __init__(
        self,
        recording: BaseRecording,
        segment_index: int = 0,
        return_scaled: bool = False,
        buffer_gb: Optional[float] = None,
        buffer_shape: Optional[tuple] = None,
        chunk_mb: Optional[float] = None,
        chunk_shape: Optional[tuple] = None,
        display_progress: bool = False,
        progress_bar_options: Optional[dict] = None,
    ):
        """
        Initialize an Iterable object which returns DataChunks with data and their selections on each iteration.

        Parameters
        ----------
        recording : si.BaseRecording
            The SpikeInterfaceRecording object which handles the data access.
        segment_index : int, optional
            The recording segment to iterate on.
            Defaults to 0.
        return_scaled : bool, optional
            Whether to return the trace data in scaled units (uV, if True) or in the raw data type (if False).
            Defaults to False.
        buffer_gb : float, optional
            The upper bound on size in gigabytes (GB) of each selection from the iteration.
            The buffer_shape will be set implicitly by this argument.
            Cannot be set if `buffer_shape` is also specified.
            The default is 1GB.
        buffer_shape : tuple, optional
            Manual specification of buffer shape to return on each iteration.
            Must be a multiple of chunk_shape along each axis.
            Cannot be set if `buffer_gb` is also specified.
            The default is None.
        chunk_mb : float, optional
            The upper bound on size in megabytes (MB) of the internal chunk for the HDF5 dataset.
            The chunk_shape will be set implicitly by this argument.
            Cannot be set if `chunk_shape` is also specified.
            The default is 1MB, as recommended by the HDF5 group. For more details, see
            https://support.hdfgroup.org/HDF5/doc/TechNotes/TechNote-HDF5-ImprovingIOPerformanceCompressedDatasets.pdf
        chunk_shape : tuple, optional
            Manual specification of the internal chunk shape for the HDF5 dataset.
            Cannot be set if `chunk_mb` is also specified.
            The default is None.
        display_progress : bool, optional
            Display a progress bar with iteration rate and estimated completion time.
        progress_bar_options : dict, optional
            Dictionary of keyword arguments to be passed directly to tqdm.
            See https://github.com/tqdm/tqdm#parameters for options.
        """
        self.recording = recording
        self.segment_index = segment_index
        self.return_scaled = return_scaled
        self.channel_ids = recording.get_channel_ids()
        super().__init__(
            buffer_gb=buffer_gb,
            buffer_shape=buffer_shape,
            chunk_mb=chunk_mb,
            chunk_shape=chunk_shape,
            display_progress=display_progress,
            progress_bar_options=progress_bar_options,
        )

    def _get_data(self, selection: Tuple[slice]) -> Iterable:
        return self.recording.get_traces(
            segment_index=self.segment_index,
            channel_ids=self.channel_ids[selection[1]],
            start_frame=selection[0].start,
            end_frame=selection[0].stop,
            return_scaled=self.return_scaled,
        )

    def _get_dtype(self):
        return self.recording.get_dtype()

    def _get_maxshape(self):
        return (
            self.recording.get_num_samples(segment_index=self.segment_index),
            self.recording.get_num_channels(),
        )


class TimestampsExtractor(BaseRecording):
    def __init__(
        self,
        file_path,
        sampling_frequency=30e3,
    ):
        time = readTrodesExtractedDataFile(file_path)
        dtype = time["data"]["systime"].dtype

        BaseRecording.__init__(self, sampling_frequency, channel_ids=[0], dtype=dtype)

        rec_segment = TimestampsSegment(
            datfile=file_path,
            sampling_frequency=sampling_frequency,
            t_start=None,
            dtype=dtype,
        )
        self.add_recording_segment(rec_segment)


class TimestampsSegment(BaseRecordingSegment):
    def __init__(self, datfile, sampling_frequency, t_start, dtype):
        BaseRecordingSegment.__init__(
            self, sampling_frequency=sampling_frequency, t_start=t_start
        )
        time = readTrodesExtractedDataFile(datfile)
        self._timeseries = generate_ephys_timestamps(time)

    def get_num_samples(self) -> int:
        return self._timeseries.shape[0]

    def get_traces(
        self,
        start_frame: Union[int, None] = None,
        end_frame: Union[int, None] = None,
        channel_indices: Union[List, None] = None,
    ) -> np.ndarray:
        traces = np.squeeze(self._timeseries[start_frame:end_frame])
        return traces


from scipy.stats import linregress


def generate_ephys_timestamps(t_ephys):
    systime_seconds = t_ephys["data"]["systime"] * 1e-9
    trodestime_index = t_ephys["data"]["time"]

    slope, intercept, _, _, _ = linregress(trodestime_index, systime_seconds)
    adjusted_timestamps = intercept + slope * trodestime_index

    return adjusted_timestamps


class TimestampsDataChunkIterator(GenericDataChunkIterator):
    """DataChunkIterator specifically for use on RecordingExtractor objects."""

    def __init__(
        self,
        recording: BaseRecording,
        segment_index: int = 0,
        return_scaled: bool = False,
        buffer_gb: Optional[float] = None,
        buffer_shape: Optional[tuple] = None,
        chunk_mb: Optional[float] = None,
        chunk_shape: Optional[tuple] = None,
        display_progress: bool = False,
        progress_bar_options: Optional[dict] = None,
    ):
        """
        Initialize an Iterable object which returns DataChunks with data and their selections on each iteration.

        Parameters
        ----------
        recording : BaseRecording
            handles the data access.
        segment_index : int, optional
            The recording segment to iterate on.
            Defaults to 0.
        return_scaled : bool, optional
            Whether to return the trace data in scaled units (uV, if True) or in the raw data type (if False).
            Defaults to False.
        buffer_gb : float, optional
            The upper bound on size in gigabytes (GB) of each selection from the iteration.
            The buffer_shape will be set implicitly by this argument.
            Cannot be set if `buffer_shape` is also specified.
            The default is 1GB.
        buffer_shape : tuple, optional
            Manual specification of buffer shape to return on each iteration.
            Must be a multiple of chunk_shape along each axis.
            Cannot be set if `buffer_gb` is also specified.
            The default is None.
        chunk_mb : float, optional
            The upper bound on size in megabytes (MB) of the internal chunk for the HDF5 dataset.
            The chunk_shape will be set implicitly by this argument.
            Cannot be set if `chunk_shape` is also specified.
            The default is 1MB, as recommended by the HDF5 group. For more details, see
            https://support.hdfgroup.org/HDF5/doc/TechNotes/TechNote-HDF5-ImprovingIOPerformanceCompressedDatasets.pdf
        chunk_shape : tuple, optional
            Manual specification of the internal chunk shape for the HDF5 dataset.
            Cannot be set if `chunk_mb` is also specified.
            The default is None.
        display_progress : bool, optional
            Display a progress bar with iteration rate and estimated completion time.
        progress_bar_options : dict, optional
            Dictionary of keyword arguments to be passed directly to tqdm.
            See https://github.com/tqdm/tqdm#parameters for options.
        """
        self.recording = recording
        self.segment_index = segment_index
        self.return_scaled = return_scaled
        self.channel_ids = recording.get_channel_ids()
        super().__init__(
            buffer_gb=buffer_gb,
            buffer_shape=buffer_shape,
            chunk_mb=chunk_mb,
            chunk_shape=chunk_shape,
            display_progress=display_progress,
            progress_bar_options=progress_bar_options,
        )

    # change channel id to always be first channel
    def _get_data(self, selection: Tuple[slice]) -> Iterable:
        return self.recording.get_traces(
            segment_index=self.segment_index,
            channel_ids=[0],
            start_frame=selection[0].start,
            end_frame=selection[0].stop,
            return_scaled=self.return_scaled,
        )

    def _get_dtype(self):
        return self.recording.get_dtype()

    # remove the last dim for the timestamps since it is always just a 1D vector
    def _get_maxshape(self):
        return (self.recording.get_num_samples(segment_index=self.segment_index),)


def ptp_time_to_datetime(ptp_time, time_zone="America/Los_Angeles"):
    """
    Convert PTP (Precision Time Protocol) time in nanoseconds to a datetime object.
    Allows specification of the time zone.
    """
    # Ensure the input is a native Python integer
    ptp_time = int(ptp_time)

    # Convert nanoseconds to seconds (integer part) and remaining nanoseconds
    seconds = ptp_time // 1_000_000_000
    nanoseconds = ptp_time % 1_000_000_000

    # Create a datetime object for the Unix epoch in UTC
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)

    # Add seconds and nanoseconds to the epoch
    utc_datetime = epoch + timedelta(seconds=seconds, microseconds=nanoseconds / 1000)

    # Convert to the specified time zone
    target_time_zone = pytz.timezone(time_zone)
    local_datetime = utc_datetime.astimezone(target_time_zone)

    return local_datetime
