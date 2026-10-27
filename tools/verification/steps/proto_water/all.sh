#!/bin/zsh
BANK=0 PREFIX=pw_nobank /tmp/protow/run.sh
BANK=1 PREFIX=pw_full /tmp/protow/run.sh
STAGE=1 BANK=1 PREFIX=pw_stage /tmp/protow/run.sh
echo allfinished > /tmp/protow.all
