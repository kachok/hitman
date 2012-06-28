#! /usr/bin/env bash

python multi_test.py

python buffer_update.py

psql -h localhost -d tweets_es -f ../db/10sentences_to_similar.sql                

#python pay_for_first10_tasks.py

#psql -h localhost -d mturk -f syn_voc_link.sql

