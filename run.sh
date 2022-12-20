# command to
#$ git pull origin; bash run.sh
#$ git pull origin && bash run.sh

git checkout redesign

# update submodule repo
(
cd misp-warninglists || exit
git pull origin
)
./.venv_submodule/bin/pip3 install -r misp-warninglists/requirements.txt


# generate updated warning lists
bash generate_lists.sh
.venv/bin/python3 merge_lists.py --warninglists misp
.venv/bin/python3 merge_lists.py --warninglists tsec

# remove generated lists and logs from the submodule
# (
# cd misp-warninglists_submodule || exit
# git restore .
# )

# save lists back to repor
git add lists/*
# git add .
git commit -m"automatic warning-list update"
git push origin
