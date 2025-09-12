# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Tuple
import xml.etree.ElementTree as ET


def _chunked(seq: List[ET.Element], n: int) -> Iterable[List[ET.Element]]:
    """Yield consecutive chunks (size n) from seq."""
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def _indent(elem: ET.Element) -> None:
    """Pretty-print in place (Python 3.9+ has ET.indent, but this is portable)."""

    def _recurse(e: ET.Element, level: int = 0) -> None:
        i = "\n" + level * "  "
        if len(e):
            if not e.text or not e.text.strip():
                e.text = i + "  "
            for child in e:
                _recurse(child, level + 1)
            if not e.tail or not e.tail.strip():
                e.tail = i
        else:
            if level and (not e.tail or not e.tail.strip()):
                e.tail = i

    _recurse(elem)


def merge_spike_ntrodes_text(
    xml_text: str,
    group_size: int = 8,
    expected_channels_per_original: Optional[int] = 4,
    reassign_ids_from: int = 1,
) -> str:
    """Merge SpikeNTrode elements in groups into 32-channel trodes.

    Parameters
    ----------
    xml_text : str
        Full XML document as a string.
    group_size : int, optional
        Number of consecutive `<SpikeNTrode>` elements to merge into one.
        Default is 8.
    expected_channels_per_original : int, optional
        If provided, validate each original `<SpikeNTrode>` has this many
        `<SpikeChannel>` children. Set to None to skip validation.
        Default is 4.
    reassign_ids_from : int, optional
        New `<SpikeNTrode id="...">` values will be reassigned starting at this
        integer. Default is 1.

    Returns
    -------
    str
        A pretty-printed XML document string with merged `<SpikeNTrode>` elements.

    Notes
    -----
    - The merged `<SpikeNTrode>` inherits attributes from the first trode in its group
      (including color, filters, etc.). Only `id` is reassigned.
    - `<SpikeChannel>` children are concatenated in input order (group order
      followed by per-trode order).
    - If the final group is smaller than `group_size`, it is still merged as-is.
    """
    # Parse
    root = ET.fromstring(xml_text)

    # Locate the SpikeConfiguration node (assumed unique/top-level in example)
    spike_cfg = root
    if spike_cfg.tag != "SpikeConfiguration":
        # If provided snippet is part of a larger file, find it by tag.
        found = root.findall(".//SpikeConfiguration")
        if not found:
            raise ValueError("No <SpikeConfiguration> element found.")
        spike_cfg = found[0]

    # Collect all immediate child SpikeNTrode elements in order
    trodes: List[ET.Element] = [e for e in list(spike_cfg) if e.tag == "SpikeNTrode"]

    if not trodes:
        return xml_text  # Nothing to do

    # Optional: validate original channel counts
    if expected_channels_per_original is not None:
        for t in trodes:
            ch_count = sum(1 for c in t if c.tag == "SpikeChannel")
            if ch_count != expected_channels_per_original:
                raise ValueError(
                    f"SpikeNTrode id={t.attrib.get('id','?')} has {ch_count} channels; "
                    f"expected {expected_channels_per_original}."
                )

    # We will rebuild: remove original trodes, then append merged ones
    # Preserve any non-SpikeNTrode children (if ever present)
    non_trode_children = [e for e in list(spike_cfg) if e.tag != "SpikeNTrode"]
    for child in list(spike_cfg):
        spike_cfg.remove(child)

    # Append back non-trode children first (preserve original relative order)
    for e in non_trode_children:
        spike_cfg.append(e)

    # Build merged trodes
    next_id = reassign_ids_from
    for group in _chunked(trodes, group_size):
        # New trode inherits attributes from the first in the group
        first = group[0]
        new_trode = ET.Element("SpikeNTrode", attrib=first.attrib.copy())
        new_trode.set("id", str(next_id))  # reassign id

        # Concatenate channels from all trodes in the group, preserving order
        for trode in group:
            for ch in trode:
                if ch.tag == "SpikeChannel":
                    # Append a shallow copy to avoid moving original nodes
                    new_trode.append(
                        ET.Element("SpikeChannel", attrib=ch.attrib.copy())
                    )

        # Append merged trode to configuration
        spike_cfg.append(new_trode)
        next_id += 1

    # Pretty print
    _indent(root)
    return ET.tostring(root, encoding="unicode")


def merge_spike_ntrodes_file(
    input_path: str | Path,
    output_path: str | Path,
    group_size: int = 8,
    expected_channels_per_original: Optional[int] = 4,
    reassign_ids_from: int = 1,
) -> None:
    """File-based convenience wrapper for merging SpikeNTrodes.

    # Example usage:
    merge_spike_ntrodes_file("L14.trodesconf", "L14_reconfig.trodesconf", group_size=8)

    Parameters
    ----------
    input_path : str | Path
        Path to input XML file.
    output_path : str | Path
        Path to write the merged XML file.
    group_size : int, optional
        Number of consecutive `<SpikeNTrode>` elements to merge. Default is 8.
    expected_channels_per_original : int, optional
        Validate each original trode has this many channels, or None to skip.
        Default is 4.
    reassign_ids_from : int, optional
        New trode ids start from this value. Default is 1.
    """
    xml_text = Path(input_path).read_text(encoding="utf-8")
    merged = merge_spike_ntrodes_text(
        xml_text=xml_text,
        group_size=group_size,
        expected_channels_per_original=expected_channels_per_original,
        reassign_ids_from=reassign_ids_from,
    )
    Path(output_path).write_text(merged, encoding="utf-8")
