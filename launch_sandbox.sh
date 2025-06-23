#!/bin/bash
# Usage: ./launch_sandbox.sh [CPU] [MEMORY]
# Example: ./launch_sandbox.sh 1.0 3.5G
CPU=${1:-1.0}
MEM=${2:-3.5G}

mkdir -p notebooks

docker run --rm -it \
  --name ml-sandbox-jupyter \
  -p 8888:8888 \
  -v "$PWD/notebooks":/tf/notebooks \
  --cpus="$CPU" --memory="$MEM" \
  tensorflow/tensorflow:2.12.0-jupyter \
  bash -c "pip install intel-openmp && jupyter lab --notebook-dir=/tf/notebooks --ip=0.0.0.0 --no-browser --allow-root"
