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
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1

date
hostname
pwd

module load conda
module load cuda
cd /blue/guralnick/rafe.lafrance/LabelLlama

uv run /blue/guralnick/rafe.lafrance/LabelLlama/llama/local/ocr_images.py \
    --image-glob '/blue/guralnick/share/fsca_01/**/*' \
    --ocr-file "$data_dir"/ocr_images_260808.csv \
    --prompt-md prompts/ocr_v2.md \
    --model-id gemma-4-E4B-it-Q8_0 \
    --api-host http://localhost:8080/v1 \
    --temperature 0.1 \
    --max-tokens 2048 \
    --threads 4 \
    --timeout 180 \
    --notes "Try using llama.cpp with a model that works with it." \
    --log-file "$data_dir"/ocr_imaging.log

date
