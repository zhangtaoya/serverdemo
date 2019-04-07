#!/usr/bin/env python
# -*- coding:utf-8 -*-
import motor.motor_tornado
from tornado import gen
import logging
from bson.json_util import dumps
from pymongo.errors import PyMongoError, AutoReconnect, OperationFailure, BulkWriteError


# To create an authenticated connection use a MongoDB connection URI:
# uri = "mongodb://user:pass@localhost:27017"
def mongo_collection(db_name, col_name, host, port):
    try:
        db_connection = motor.motor_tornado.MotorClient(host, port)
        db = db_connection.get_database(db_name)
        col = db[col_name]
    except AutoReconnect as e:
        logging.error('connect failed, host %s, port %d, %s' % (host, port, str(e)))
        return None

    return col


def mongo_db(db_name, host, port):
    try:
        db_connection = motor.motor_tornado.MotorClient(host, port)
        db = db_connection.get_database(db_name)
    except AutoReconnect as e:
        logging.error('connect failed, host %s, port %d, %s' % (host, port, str(e)))
        return None

    return db


@gen.coroutine
def mongo_insert_one(col, item, returnid=False):
    try:
        ret = yield col.insert_one(item)
        if returnid:
            raise gen.Return(ret.inserted_id)
        else:
            raise gen.Return(True)
    except (OperationFailure, AutoReconnect) as e:
        stritem = dumps(item)
        logging.warning("mongo_insert failed, item %s, reason %s" % (stritem[0:10240], str(e)))
        raise gen.Return(False)


@gen.coroutine
def mongo_insert_many(col, item):
    try:
        yield col.insert_many(item)
        raise gen.Return(True)
    except (OperationFailure, AutoReconnect) as e:
        stritem = dumps(item)
        logging.error("mongo_insert failed, item %s, reason %s" % (stritem[0:10240], str(e)))
        raise gen.Return(False)


@gen.coroutine
def mongo_find_one(col, query, projection=None):
    try:
        if projection:
            r = yield col.find_one(query, projection=projection)
        else:
            r = yield col.find_one(query)
        raise gen.Return(r)
    except PyMongoError as e:
        logging.error("mongo_find_one failed, query %s, reason %s" % (dumps(query), str(e)))
        raise gen.Return(False)


@gen.coroutine
def mongo_update(col, query, update, up=False):
    try:
        yield col.update_many(query, update, upsert=up)
        raise gen.Return(True)
    except PyMongoError as e:
        logging.error("mongo_update failed, query %s, reason %s" % (dumps(query), str(e)))
        raise gen.Return(False)


@gen.coroutine
def mongo_update_many(col, query, update, up=False):
    ret = yield mongo_update(col, query, update, up)
    raise gen.Return(ret)


@gen.coroutine
def mongo_update_one(col, query, update, up=False, returnid=False):
    try:
        ret = yield col.update_one(query, update, upsert=up)
        if up and returnid and ret:
            raise gen.Return({'matched_count': ret.matched_count, 'upserted_id': ret.upserted_id})
        else:
            raise gen.Return(True)
    except PyMongoError as e:
        logging.error("mongo_update_one failed, query %s, reason %s" % (dumps(query), str(e)))
        raise gen.Return(False)


@gen.coroutine
def mongo_delete_one(col, query):
    try:
        r = yield col.delete_one(query)
        raise gen.Return(r)
    except PyMongoError as e:
        logging.error("mongo_delete_one failed, query %s, reason %s" % (dumps(query), str(e)))
        raise gen.Return(False)


# large batches find
# def do_find():
#     cursor = db.test_collection.find({'i': {'$lt': 5}}).sort('i')
#     for document in (yield cursor.to_list(length=100)):
#     pprint.pprint(document)

#     cursor = db.test_collection.find({'i': {'$lt': 5}}).sort('i')
#     for document in (yield cursor.to_list(length=100)):
#         pprint.pprint(document)

#     cursor = db.test_collection.find({'i': {'$lt': 5}})
#     while (yield cursor.fetch_next):
#         document = cursor.next_object()

@gen.coroutine
def mongo_find(col, query, projection=None):
    try:
        if projection:
            cursor = col.find(query, projection=projection)
        else:
            cursor = col.find(query)
        docs = yield cursor.to_list(None)
        raise gen.Return(docs)
    except PyMongoError as e:
        logging.error("mongo_find failed, query %s, reason %s" % (dumps(query), str(e)))
        raise gen.Return(False)


@gen.coroutine
def mongo_find_limit(col, query, limit, projection=None):
    try:
        if projection:
            cursor = col.find(query, projection=projection).limit(limit)
        else:
            cursor = col.find(query).limit(limit)
        docs = yield cursor.to_list(None)
        raise gen.Return(docs)
    except PyMongoError as e:
        logging.error("mongo_find failed, query %s, reason %s" % (dumps(query), str(e)))
        raise gen.Return(False)


@gen.coroutine
def mongo_find_count(col, query):
    try:
        r = yield col.find(query).count()
        raise gen.Return(r)
    except PyMongoError as e:
        logging.error("mongo_find_count failed, query %s, reason %s" % (dumps(query), str(e)))
        raise gen.Return(False)


@gen.coroutine
def mongo_find_sort(col, query, sort, projection=None):
    try:
        if projection:
            cursor = col.find(query, projection=projection).sort(sort)
        else:
            cursor = col.find(query).sort(sort)
        docs = yield cursor.to_list(None)
        raise gen.Return(docs)
    except PyMongoError as e:
        logging.error("mongo_find_sort failed, query %s, reason %s" % (dumps(query), str(e)))
        raise gen.Return(False)


@gen.coroutine
def mongo_find_sort_skip_limit(col, query, sort, skip, limit, projection=None):
    try:
        if projection:
            cursor = col.find(query, projection=projection).sort(sort).skip(skip).limit(limit)
        else:
            cursor = col.find(query).sort(sort).skip(skip).limit(limit)
        docs = yield cursor.to_list(None)
        raise gen.Return(docs)
    except PyMongoError as e:
        logging.error("mongo_find_sort_skip_limit failed, query %s, reason %s" % (dumps(query), str(e)))
        raise gen.Return(False)


@gen.coroutine
def mongo_find_one_and_update(col, query, update, upsert=True, return_document=True):
    try:
        r = yield col.find_one_and_update(query, update, upsert=upsert, return_document=return_document)
        raise gen.Return(r)
    except (OperationFailure, AutoReconnect) as e:
        logging.error("mongo_find_and_modify failed, query %s, reason %s" % (dumps(query), str(e)))
        raise gen.Return(None)


@gen.coroutine
def mongo_delete(col, query):
    try:
        r = yield col.delete_many(query)
        raise gen.Return(r)
    except PyMongoError as e:
        logging.error("mongo_delete failed, query %s, reason %s" % (dumps(query), str(e)))
        raise gen.Return(False)


@gen.coroutine
def mongo_aggregate(col, pipeline):
    try:
        cursor = col.aggregate(pipeline)
        docs = yield cursor.to_list(None)
        raise gen.Return(docs)
    except PyMongoError as e:
        logging.error("mongo_aggregate failed, pipeline %s, reason %s" % (dumps(pipeline), str(e)))
        raise gen.Return(False)


@gen.coroutine
def mongo_batchupdate(col, updatas, upsert=False, ordered=True):
    if not updatas:
        raise gen.Return(True)
    if ordered:
        bulk = col.initialize_ordered_bulk_op()
    else:
        bulk = col.initialize_unordered_bulk_op()
    if upsert:
        for item in updatas:
            bulk.find(item[0]).upsert().update(item[1])
    else:
        for item in updatas:
            bulk.find(item[0]).update(item[1])
    try:
        yield bulk.execute()
        raise gen.Return(True)
    except BulkWriteError as bwe:
        logging.error("mongo_batchupdate failed, updatas %s, reason %s" % (dumps(updatas), str(bwe.details)))
        raise gen.Return(False)


@gen.coroutine
def mongo_group(col, para_key, para_condition, para_initial, para_reduce):
    try:
        r = yield col.group(para_key, para_condition, para_initial, para_reduce)
        raise gen.Return(r)
    except PyMongoError as e:
        logging.error("mongo_group failed, key %s, condition %s, initial %s, reduce %s, reason %s" % (
            dumps(para_key), dumps(para_condition), dumps(para_initial), dumps(para_reduce), str(e)))
        raise gen.Return(False)
