#!/bin/bash

#SBATCH --job-name=wrangle_fsca_01

#SBATCH --mail-user=rafe.lafrance@ufl.edu
#SBATCH --mail-type=ALL
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --output=/blue/guralnick/rafe.lafrance/LabelLlama/logs/%x_%j.out

#SBATCH --cpus-per-task=1
#SBATCH --mem=16gb
#SBATCH --time=4-00:00:00

date
hostname
pwd

module load conda
cd /blue/guralnick/rafe.lafrance/LabelLlama

uv run /blue/guralnick/rafe.lafrance/LabelLlama/llama/diode/wrangle_images.py \
    --zip-glob '/blue/guralnick/share/diode/fsca_01/*.zip'  \
    --image-regex  '_card.jpg' \
    --root-dir '/blue/guralnick/share/diode/fsca_01'

date
