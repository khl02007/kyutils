#!/usr/bin/env python
import xml.etree.ElementTree as ET
import os
import ntpath
import copy


DEFAULT_TRODE_CONF_FILE_NAME = 'livermore_trodesconf.trodesconf'
valid_probe_types = [
        '6_15',
        '4_20',
    ]

def read_input():
    """Get user input from command line

    Returns
    -------
    dictionary
        user input
    """
    valid_probes = ', '.join(valid_probe_types)

    while True:
        print("Probe count (between 1 - 8):", end=' ')
        probe_count = input()

        if not probe_count.isdigit():
            print(f'Probe count must be integer. Your value is {probe_count}')
            continue

        probe_count = int(probe_count)

        if probe_count < 1 or probe_count > 8:
            print(f'Probe count must be between 1 and 8. Your value is {probe_count}')
            continue

        print(f'Probe Type (one of [{valid_probes}]):', end=' ')
        probe_type = input()

        if not probe_type in valid_probe_types:
            probe_count_error = f'Probe type not valid. Your value is: {probe_type}'
            probe_type_error = f'Valid options must be one of: {valid_probes}'
            print(f'{probe_count_error}. {probe_type_error}')
            continue

        print('Enter file name or leave blank to use default name:', end=' ')
        trode_conf_file_name = input()

        file_name = trode_conf_file_name or DEFAULT_TRODE_CONF_FILE_NAME
        trode_file = file_name if '.trodesconf' in file_name else f'{file_name}.trodesconf'
            

        print(f'Probe count: {probe_count}')
        print(f'Probe type: {probe_type}')
        print(f'Trodes conf file name: {file_name}')

        break

    return {
        'probe_count': probe_count,
        'probe_type': probe_type,
        'trode_conf_file_name': file_name,
    }

def get_trodes_conf(size):
    """Get trodes configuration
    Parameters
    ----------
    size : str
        size of the configuration

    Returns
    -------
    Element
        configuration as an XML element
    """
    spike_conf_file = ''
    match size:
        case '4_20':
            spike_conf_file = 'spike_config_4_20.xml'
        case '6_15':
            spike_conf_file = 'spike_config_6_15.xml'
        case _:
            raise ValueError(f'{size} is not supported')
    spike_conf = ET.parse(spike_conf_file)

    return spike_conf.getroot()

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

def generate_trodes_conf_file(probe_count, spike_config):
    """_summary_

    Parameters
    ----------
    probe_count : int
        Number of probes
    spike_config : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """    
    base_config = ET.parse('trode_conf_base.xml')
    base_config_current = base_config.getroot()
    xml_elements = []

    for index in range(0, probe_count):
        hwChan_increment = 128 * index
        spike_config_items = copy.deepcopy(spike_config)
        spike_config_len = len(spike_config)

        for child in spike_config_items:
            child.attrib['id'] = str(int(child.attrib['id']) + (index * spike_config_len))

            for grand_child in child:
                hw_chan = str(int(grand_child.attrib['hwChan']) + hwChan_increment)
                grand_child.attrib['hwChan'] = hw_chan

            xml_elements.append(child)

    base_config_current.find('SpikeConfiguration').extend(xml_elements)
    return base_config_current

if __name__ == '__main__':
    user_input = read_input()
    spike_config_xml = get_trodes_conf(user_input['probe_type'])
    trodes_conf_to_create = generate_trodes_conf_file(
       user_input['probe_count'],
       spike_config_xml,
    )

    create_trode_conf_file(
        user_input['trode_conf_file_name'],
        trodes_conf_to_create,
    )
