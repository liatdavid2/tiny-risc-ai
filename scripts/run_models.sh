#!/bin/sh
set -e
python python/train_models.py
python python/run_hardware_inference.py --model all
