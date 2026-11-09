#!/bin/bash

#SBATCH --job-name=retire_zips

#SBATCH --mail-user=rafe.lafrance@ufl.edu
#SBATCH --mail-type=ALL
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --output=/blue/guralnick/rafe.lafrance/LabelLlama/logs/%x_%j.out

#SBATCH --cpus-per-task=4
#SBATCH --mem=16gb
#SBATCH --time=2:00:00

date
hostname
pwd

target="fsca_01"
mkdir /orange/guralnick/rafe.lafrance/diode_zips/"$target"
mv -v /blue/guralnick/share/diode/"$target"/*.zip /orange/guralnick/rafe.lafrance/diode_zips/"$target"/

date
