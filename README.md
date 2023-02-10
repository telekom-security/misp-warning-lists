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
- Updating warninglists
  - `$ ./run.sh`
    - pull submodule misp-warninglist
    - generate lists in both sources (tsec-warninglists and misp-warninglist)
    - merges generated lists to the main _list_ directory
    - commit changes to git repository
- The script `create_or_update_env.sh` creates two python virtual environments and install modules from the related requirements.txt:
  - .venv_submodule: for running scripts in the misp-warninglist submodule
  - .venv: for running rest of the application
- The project contains submodule and it is not automatically downloaded if you just `$ git clone <url>`
  - do instead `$ git clone --recurse-submodules <url>`

