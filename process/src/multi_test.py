# -*- coding: utf-8 -*-
from settings import settings
import psycopg2

from psycopg2.pool import PersistentConnectionPool
from psycopg2.pool import ThreadedConnectionPool

import logging
import argparse

import mturk

import threading

import Queue


def do_work(conn, item):
	cur=conn.cursor()
	sql="INSERT INTO multi_test (value) VALUES (%s);"
	cur.execute(sql, (item["id"],))
	conn.commit()

def worker():
	while True:
		item = q.get()
		
		print "thread: ", threading.currentThread().name
		
		conn=conn_pool.getconn()
		
		do_work(conn, item)
		q.task_done()


num_worker_threads=10


q = Queue.Queue()
mturk_conn=mturk.conn()


conn_pool=PersistentConnectionPool(10, 20,database=settings["dbname"], user=settings["user"], host=settings["host"])


for i in range(num_worker_threads):
	t = threading.Thread(target=worker)
	t.daemon = True
	t.start()

for i in range(1000):
	item={}
	item["id"]=i
	q.put(item)

q.join()       # block until all tasks are done