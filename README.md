# misp-warning-lists
This project allows periodical update of MISP warninglists, monitoring their generations and storing them directly in this git repository.
The generated warning lists comes from the official [MISP warning list repository](https://github.com/MISP/misp-warninglists) as well as from custom scripts.

# Project structure
- __lists/__: this directory contains the most recent versions of all the available warninglists
- process of updating warninglists:
  - __generating updates__
    - the script `generate_lists.sh` runs all the generation scripts in `./misp-warninglists_submodule/` and `./tsec-warninglists/`. 
    - The generated warning lists are stored in the corresponding subfolders `./lists/`. 
  - __merging updates__
    - the script `merge_lists.py` copies selected warninglists from the subdirectories to the main directory
- `./misp-warninglists_submodule/`
  - is a Git submodule of the official [MISP warning list repository](https://github.com/MISP/misp-warninglists)
  - It is expected to be automatically updated very frequently and therefore do not make any changes in there (otherwise automatic updates will be more difficult).

# Operations
- The script `create_venv.sh` creates two python virtual environments (expect pyenv installed):
  - .venv_submodule: for running scripts in the misp-warninglist submodule
  - .venv: for running rest of the application
- 

# Updating warninglists
- $ bash ./generate_lists.sh
- $ .venv/bin/python3 merge_lists.py --warninglists misp
- $ .venv/bin/python3 merge_lists.py --warninglists tsec


