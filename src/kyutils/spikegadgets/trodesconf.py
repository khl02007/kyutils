from typing import List
import numpy as np
import xml.etree.ElementTree as ET

def create_trodesconf(probe_list: List, out_path: str):
    """Generate a trodesconf (XML) file based on probe type sequence.
    - This works only for Livermore probes of type 15um or 20um.
    - Can specify any sequence of the two probe types of any length.
    - Each probe will be displayed in a separate page in Trodes, with each shank in its own column.
    - The order of the channels will be from top to bottom, with the contact side facing you.
    - Each Ntrode contains 4 contacts. 
    
    Parameters
    ----------
    probe_types : iterable of 15 or 20
        example: [20,15,20] for three probe implant with 20um, 15um, 20um types (in this order)
    out_path : str
        path to save the trodesconf file
    """
    
    assert all(probe_type in [15, 20] for probe_type in probe_list), "Probe type must be either 15 or 20"

    base = ET.parse('trode_conf_base.xml')
    base_root = base.getroot()

    StreamDisplay = base_root.find('StreamDisplay')
    StreamDisplay.attrib['pages'] = str(len(probe_list))

    HardwareConfiguration = base_root.find('HardwareConfiguration')
    HardwareConfiguration.attrib['numChannels'] = str(128*len(probe_list))

    SpikeConfiguration = base_root.find('SpikeConfiguration')
    for probe_idx in range(len(probe_list)):
        probe_type = probe_list[probe_idx]
        if probe_type == 20:
            probe_root = ET.parse('spike_config_20.xml').getroot()
        elif probe_type == 15:
            probe_root = ET.parse('spike_config_15.xml').getroot()
        for SpikeNTrode in probe_root.findall('.//SpikeNTrode'):
            SpikeNTrode.attrib['id'] = str(int(SpikeNTrode.attrib['id'])+32*probe_idx)
            for SpikeChannel in SpikeNTrode.findall('SpikeChannel'):
                SpikeChannel.attrib['hwChan'] = str(int(SpikeChannel.attrib['hwChan'])+128*probe_idx)
            SpikeConfiguration.append(SpikeNTrode)

    indent(base_root)
    
    base.write(out_path, encoding='utf-8', xml_declaration=True)
    
def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i