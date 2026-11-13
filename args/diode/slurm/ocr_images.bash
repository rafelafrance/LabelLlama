#!/bin/bash

#SBATCH --job-name=ocr_images

#SBATCH --mail-user=rafe.lafrance@ufl.edu
#SBATCH --mail-type=ALL
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --output=/blue/guralnick/rafe.lafrance/LabelLlama/logs/%x_%j.out

#SBATCH --cpus-per-task=4
#SBATCH --mem=16gb
#SBATCH --time=4-00:00:00
#SBATCH --partition=hpg-rtx6000
#SBATCH --gres=gpu:1

date
hostname
pwd

module purge
module load conda cuda
cd /blue/guralnick/rafe.lafrance/LabelLlama

source /home/rafe.lafrance/hf
source /blue/guralnick/rafe.lafrance/LabelLlama/.venv/bin/activate

export TRITON_DEFAULT_FP_FUSION=1

# export PATH=/blue/guralnick/rafe.lafrance/LabelLlama/.venv/bin:$PATH

uv run /blue/guralnick/rafe.lafrance/LabelLlama/llama/pipelines/ocr_images.py \
    --image-glob '/blue/guralnick/share/diode/fsca_01/**/*' \
    --ocr-file /blue/guralnick/rafe.lafrance/LabelLlama/data/diode/ocr_images_fsca_01a.csv \
    --prompt-md prompts/ocr_v2.md \
    --model-id Qwen/Qwen3.5-4B \
    --max-tokens 2048 \
    --threads 4 \
    --limit 10

date

    # --model-id Qwen/Qwen3.6-35B-A3B \
