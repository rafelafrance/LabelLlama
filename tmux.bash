#!/bin/bash

SESSION="llama"
ROOT="$HOME/work/language_models"

tmux new -s $SESSION -d
tmux rename-window -t $SESSION llama
tmux send-keys -t $SESSION "cd $ROOT/LabelLlama" C-m
tmux send-keys -t $SESSION "vv" C-m
tmux send-keys -t $SESSION "git status" C-m

tmux new-window -t $SESSION
tmux send-keys -t $SESSION "cd $ROOT/LabelLlama" C-m
tmux send-keys -t $SESSION "vv" C-m

tmux select-window -t $SESSION:1
tmux attach -t $SESSION
