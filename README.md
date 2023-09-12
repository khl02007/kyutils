# kyutils

kyu's utils

some examples:
- probe generator: generates `probeinterface.Probe` objects for the 15um and 20um versions of the Livermore polymer probes
- trodesconf generators:
  - generates a trodesconf file based on a list of Livermore probe types; e.g. if implanting three Livermore probes (one 15um type and two 20um type) in alternating order, can pass the list `[20, 15, 20]` and will generate a trodesconf file with the contacts arranged geometrically
  - generate a trodesconf file given the number of channels; good for reconfiguring
- header parser: parses the header of a SpikeGadgets `rec` file
- behavior parser: given the extracted DIO dat files from a SpikeGadgets `rec` file, plots the time course of the animal's decisions in the W-track task and indicates rewarded trials

installation:
`pip install kyutils`

for the version that creates figurl, `pip install "kyutils[figurl]"` and set up kachery cloud.