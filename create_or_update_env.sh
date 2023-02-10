main_venv_dir='./.venv/'
main_requirements_txt='./requirements.txt'

submodule_venv_dir='./.venv_submodule/'
submodule_dir='./misp-warninglists/'
submodule_requirements_txt='./misp-warninglists/requirements.txt'

# ------ MAIN ENV ------
if [ ! -d "$main_venv_dir" ]; then
  python3 -m venv "$main_venv_dir"
fi
"$main_venv_dir"/bin/python3 -m pip install --upgrade pip
"$main_venv_dir"/bin/python3 -m pip install -r $main_requirements_txt


# ------ SUBMODULE ENV ------
# create venv
if [ ! -d "$submodule_venv_dir" ]; then
  python3 -m venv "$submodule_venv_dir"
fi
"$submodule_venv_dir"/bin/python3 -m pip install --upgrade pip

# "$submodule_venv_dir"/bin/python3 -m pip install -r $submodule_requirements_txt
# this hack install requirements.txt but replace "pyOpenSSL==19.1.0" by "pyOpenSSL" (because it is somehow broken version)
while read req; do
  if [ "$req" = "pyOpenSSL==19.1.0" ]; then
    "$submodule_venv_dir"/bin/python3 -m pip install pyOpenSSL
  else
    "$submodule_venv_dir"/bin/python3 -m pip install "$req"
  fi
done < $submodule_requirements_txt


# other requirements in submodule: sponge
if ! [ -x "$(command -v sponge)" ]; then
   echo "sudo apt install moreutils" # the atp command should be directly executed but I am not sure about the sudo rights
fi


# --- Check if we can write to log file ---
# if exist $WARNINGLISTS_LOG_FILE ...
