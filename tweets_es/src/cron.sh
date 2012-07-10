#! /usr/bin/env bash

python multi_test.py

python buffer_update.py

psql -h localhost -d tweets_es -f ../db/10sentences_to_similar.sql                

python generate_similar_hits.py

python add_similar_hits_to_mturk.py

#psql -h localhost -d mturk -f ../db/grade_qc.sql

#python process_qc.py

#psql -h localhost -d mturk -f ../db/update_10sentences_from_qc.sql




#python pay_for_first10_tasks.py

#psql -h localhost -d mturk -f syn_voc_link.sql

