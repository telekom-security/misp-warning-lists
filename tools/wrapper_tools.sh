set_python_wrapper(){
  # sets $python_wrapper instead of symlink from $bin_dir to python binary
  bin_dir=$1
  python_wrapper=$2

  if [[ "$(readlink "$bin_dir"/python)" == "python3" ]];
  then
      python_original="python3"
  else
      python_original="python"
  fi

  if [ ! -f "$bin_dir"/python_original ]
  then
    mv "$bin_dir"/$python_original "$bin_dir"/python_original
    ln -s "$PWD"/"$python_wrapper" "$PWD"/"$bin_dir"/$python_original
  fi
}

unset_python_wrapper(){
  bin_dir=$1
  if [[ "$(readlink "$bin_dir"/python)" == "python3" ]];
  then
      python_original="python3"
  else
      python_original="python"
  fi

  if [ -f "$bin_dir"/python_original ]
  then
    mv "$bin_dir"/python_original "$bin_dir"/$python_original
  fi
}