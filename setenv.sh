export LCG_RELEASE_DIR=/cvmfs/sft.cern.ch/lcg/views/LCG_102/x86_64-centos7-gcc8-opt

export PIXEL_MONITORING_DIR=${PWD}

export PYTHONPATH=${PYTHONPATH}:${PWD}
export PYTHONPATH=${PYTHONPATH}:${PWD}/external
export PYTHONPATH=${PYTHONPATH}:${PWD}/src

source ${LCG_RELEASE_DIR}/setup.sh
