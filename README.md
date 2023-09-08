# kyutils

kyu's utils

some examples:
- trodesconf generator:
  - generates a trodesconf file based on a list of probe types; e.g. if implanting three probes (1 15um type and 2 20um type) in alternating order, can pass the list `[20, 15, 20]` and will generate a trodesconf file with the contacts arranged geometrically
  - generate a trodesconf file given the number of channels; good for reconfiguring
- header parser: parses the header of a rec file
- behavior parser: given the extracted dat files for DIO from a spikegadgets rec file, plots the time course of animal's decisions in the w-track and whether it was rewarded