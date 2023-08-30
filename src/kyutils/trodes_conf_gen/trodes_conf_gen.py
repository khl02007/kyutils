#!/usr/bin/env python
import xml.etree.ElementTree as ET
import os
import ntpath
import copy

valid_probe_types = [15, 20]

def get_sibling_file(file_name):
    file_directory = os.path.dirname(__file__)
    return os.path.join(file_directory, file_name)
    

def get_spike_conf_roots(probe_types):
    """_summary_

    Parameters
    ----------
    probe_types : list[int]
        List of type of probe

    Returns
    -------
    xmlElement
        XML roots
    """    
    spike_conf_roots = []
    

    for probe_type in probe_types:
        spike_conf_file = get_sibling_file(f'spike_config_{probe_type}.xml')
        spike_conf = ET.parse(spike_conf_file)
        spike_conf_roots.append(spike_conf.getroot())
    
    return spike_conf_roots

def get_download_folder():
    """get download folder

    Returns
    -------
    str
        Download folder
    """
    windows_download_folder = f'{os.getenv("USERPROFILE")}\\Downloads'
    unix_download_folder = f'{os.getenv("HOME")}/Downloads'

    return windows_download_folder if os.name == 'nt' else unix_download_folder

def create_trode_conf_file(trodes_file_name, trodes_conf_xml_root):
    """Create trodes conf XML file

    Parameters
    ----------
    trodes_conf_xml_root : Element
        Element object
    """
    download_file = os.path.join(get_download_folder(), trodes_file_name)
    tree = ET.ElementTree(trodes_conf_xml_root)
    with open(download_file, 'wb') as file:
        tree.write(file, encoding='utf-8')
    print(f'File written to - {download_file}')

def generate_trodes_conf_file(spike_conf_roots):
    """generate trodes conf file

    Parameters
    ----------
    spike_conf_roots : list[xmlElement]
       list of xmlElement roots

    Returns
    -------
    xmlElement
        File to generate
    """    
    base_config = ET.parse(get_sibling_file('trode_conf_base.xml'))
    base_config_current = copy.deepcopy(base_config.getroot())
    xml_elements = []
    root_count = len(spike_conf_roots)

    for index, spike_conf_root in enumerate(spike_conf_roots):
        hwChan_increment = 128 * index
        spike_config_items = copy.deepcopy(spike_conf_root)
        spike_config_len = len(spike_conf_root)

        for child in spike_config_items:
            child.attrib['id'] = str(int(child.attrib['id']) + (index * spike_config_len))

            for grand_child in child:
                hw_chan = str(int(grand_child.attrib['hwChan']) + hwChan_increment)
                grand_child.attrib['hwChan'] = hw_chan

            xml_elements.append(child)

    base_config_current.find('SpikeConfiguration').extend(xml_elements)
    base_config_current.find('StreamDisplay').attrib['pages'] = str(root_count)
    return base_config_current

def create_trode_conf_file(trodes_file_name, trodes_conf_xml_root):
    """Create trodes conf XML file

    Parameters
    ----------
    trodes_conf_xml_root : Element
        Element object
    """
    download_file = os.path.join(get_download_folder(), trodes_file_name)
    tree = ET.ElementTree(trodes_conf_xml_root)
    with open(download_file, 'wb') as file:
        tree.write(file, encoding='utf-8')
    print(f'File written to - {download_file}')

def generate_trodes_file(probes, trodes_file_name = 'livermore_trodesconf.trodesconf'):
    """Main function, generates Trodes file

    Parameters
    ----------
    probes : list[int]
        list of integers
    trodes_file_name : str, optional
        file name, by default 'livermore_trodesconf.trodesconf'

    Raises
    ------
    ValueError
        Raise error if ot all probe_types are valid
    """    
    if not all(probe in valid_probe_types for probe in probes):
        raise ValueError(f'Probe list contain an invalid value. Your input was {probes}')
    
    spike_conf_roots = get_spike_conf_roots(probes)
    trodes_conf_to_create = generate_trodes_conf_file(spike_conf_roots)
    create_trode_conf_file(
        trodes_file_name,
        trodes_conf_to_create,
    )

if __name__ == '__main__':
    probes = [15, 20]
    trodes_file_name = 'livermore_trodesconf.trodesconf'
    
    generate_trodes_file(probes, trodes_file_name)
