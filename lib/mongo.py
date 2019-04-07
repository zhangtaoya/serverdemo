#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pymongo
from pymongo.errors import PyMongoError, AutoReconnect, OperationFailure, BulkWriteError
from pymongo import MongoClient
import log
from bson.json_util import dumps


def mongo_collection(db_name, col_name, host, port):
    try:
        db_connection = MongoClient(host, port)
    except AutoReconnect as e:
        log.error('connect failed, host %s, port %d, %s' % (host, port, str(e)))
        return None

    db = pymongo.database.Database(db_connection, db_name)
    col = pymongo.collection.Collection(db, col_name)
    return col


def mongo_insert(col, item):
    try:
        col.insert(item)
        return True
    except (OperationFailure, AutoReconnect) as e:
        stritem = dumps(item)
        log.error("mongo_insert failed, item %s, reason %s" % (stritem[0:10240], str(e)))
        return False


def mongo_find_and_modify(col, query, update, upsert=True, sort=None, full_response=False, manipulate=False, **kwargs):
    try:
        r = col.find_and_modify(query, update, upsert, sort, full_response, manipulate, **kwargs)
        return r
    except (OperationFailure, AutoReconnect) as e:
        log.error("mongo_find_and_modify failed, query %s, reason %s" % (dumps(query), str(e)))
        return None


def mongo_find_one(col, query, *args, **kwargs):
    try:
        r = col.find_one(query, *args, **kwargs)
        return r
    except PyMongoError as e:
        log.error("mongo_find_one failed, query %s, reason %s" % (dumps(query), str(e)))
        return -1


def mongo_update_one(col, query, update, up=False):
    try:
        col.update_one(query, update, upsert=up)
        return True
    except PyMongoError as e:
        log.error("mongo_update_one failed, query %s, reason %s" % (dumps(query), str(e)))
        return False


def mongo_update(col, query, update, up=False):
    try:
        col.update_many(query, update, upsert=up)
        return True
    except PyMongoError as e:
        log.error("mongo_update_many failed, query %s, reason %s" % (dumps(query), str(e)))
        return False


def mongo_find(col, query, *args, **kwargs):
    try:
        r = col.find(query, *args, **kwargs)
        return r
    except PyMongoError as e:
        log.error("mongo_find failed, query %s, reason %s" % (dumps(query), str(e)))
        return -1


def mongo_find_count(col, query):
    try:
        r = col.find(query).count()
        return r
    except PyMongoError as e:
        log.error("mongo_find_count failed, query %s, reason %s" % (dumps(query), str(e)))
        return -1


def mongo_find_and_sort(col, query, sort_field, sort_dir=-1):
    try:

        if sort_dir == 1:
            sort_type = pymongo.ASCENDING
        else:
            sort_type = pymongo.DESCENDING

        r = col.find(query).sort(sort_field, sort_type)
        return r
    except PyMongoError as e:
        log.error("mongo_find_sort failed, query %s, reason %s" % (dumps(query), str(e)))
        return -1


def mongo_find_sort(col, query, sort_field):
    try:
        r = col.find(query).sort(sort_field)
        return r
    except PyMongoError as e:
        log.error("mongo_find_sort failed, query %s, reason %s" % (dumps(query), str(e)))
        return -1


def mongo_find_sort_limit(col, query, sort_field, sort_dir=-1, limit_num=500):
    try:

        if sort_dir == 1:
            sort_type = pymongo.ASCENDING
        else:
            sort_type = pymongo.DESCENDING

        if limit_num <= 0:
            limit_num = 500

        r = col.find(query).sort(sort_field, sort_type).limit(limit_num)
        return r
    except PyMongoError as e:
        log.error("mongo_find_sort failed, query %s, reason %s" % (dumps(query), str(e)))
        return -1


def mongo_find_skip_limit(col, query, skip, limit):
    try:
        r = col.find(query).skip(skip).limit(limit)
        return r
    except PyMongoError as e:
        log.error("mongo_find_skip_limit failed, query %s, reason %s" % (dumps(query), str(e)))
        return -1


def mongo_find_sort_skip_limit(col, query, sort, skip, limit):
    try:
        r = col.find(query).sort(sort).skip(skip).limit(limit)
        return r
    except PyMongoError as e:
        log.error("mongo_find_sort_skip_limit failed, query %s, reason %s" % (dumps(query), str(e)))
        return -1


def mongo_remove(col, query):
    try:
        col.remove(query)
        return True
    except PyMongoError as e:
        log.error("mongo_remove failed, query %s, reason %s" % (dumps(query), str(e)))
        return False


def mongo_batchupdate(col, updatas, upsert=False, ordered=True):
    if ordered:
        bulk = col.initialize_ordered_bulk_op()
    else:
        bulk = col.initialize_unordered_bulk_op()  # paral execute
    if upsert:
        for item in updatas:
            bulk.find(item[0]).upsert().update(item[1])
    else:
        for item in updatas:
            bulk.find(item[0]).update(item[1])
    try:
        bulk.execute()
    except BulkWriteError as bwe:
        # pprint(bwe.details)
        return bwe.details
