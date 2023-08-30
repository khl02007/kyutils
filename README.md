# kyutils

useful utils

## Trode Config Generator

This is a very simple application that takes in parameters needed to build a trodes configuration file and generates the file. 

To run the files -

- Go the home directory of this application.
  
- Navigate to src/kyutils/trodes_conf_gen
  
- Make the app executable (only needs to be done once)-

```bash
chmod +x ./trodes_conf_gen
```

- Run the app -

```bash
./trodes_conf_gen.py
```

Add the desired values. Then the printout on the screen will tell you where to find the generated configuration file.

You can also run the function

```bash
generate_trodes_file(probes, trodes_file_name = 'livermore_trodesconf.trodesconf')
```

to generate the trodes file
