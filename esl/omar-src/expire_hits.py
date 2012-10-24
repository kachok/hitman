# -*- coding: utf-8 -*-
from settings import settings
import psycopg2
from psycopg2.pool import PersistentConnectionPool
import json
import logging
import argparse
import mturk
import threading
import Queue
import datetime
import boto.mturk.connection as boto

parser = argparse.ArgumentParser(description='Get completed assignments and results from Mechanical Turk',epilog="And that's how you'd do it")

parser.add_argument('--settings', default='settings', help='filename of settings file to use: settings (.py) will be used by default')
parser.add_argument('--level',default='INFO', choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL"],help='logging level: e.g. DEBUG, INFO, etc.')
parser.add_argument('--hittype',default='ALL', choices=["ALL","VOCABULARY", "SYNONYMS"], help='get assignments for HITs of specific types: VOCABULARY, SYNONYMS or ALL')
parser.add_argument('--coverage',default='ALL', choices=["ALL","OPENONLY"], help='get assignment for all or just open HITs: ALL/OPENONLY')

args = parser.parse_args()


settings_module = __import__(args.settings) #, globals={}, locals={}, fromlist=[], level=-1
settings=settings_module.settings


conn = boto.MTurkConnection(aws_access_key_id=settings.settings["aws_access_key_id"], aws_secret_access_key=settings.settings["aws_secret_access_key"], host=settings.settings["service_url"].replace("https://",""))
 

print conn.get_all_hits()










