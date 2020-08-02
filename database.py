#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   database.py
@Author  :   Racle
@Version :   1.0
@Desc    :   None
'''

# 由于FAQ问题，数据集比较小，可以储存在redis数据库。

import redis


class RedisDb:
    def __init__(self, host, password, max_connections):
        try:
            self.__pool = redis.ConnectionPool(
                host=host,
                port=6379,
                password=password,
                db=0,
                max_connections=max_connections
            )
        except Exception as e:
            print(e)

    def insert(self, id, question, answer):
        connection = redis.Redis(connection_pool=self.__pool)
        try:
            connection.hmset(id, {
                "question": question,
                "answer": answer
            })
        except Exception as e:
            print(e)
        finally:
            del connection

    def search_by_id(self, id):
        connection = redis.Redis(connection_pool=self.__pool)
        try:
            res = connection.hmget(id, [
                "question",
                "answer"
            ])
        except Exception as e:
            print(e)
            res = [None, None]
        finally:
            del connection
        return res

    def delete_cache(self, id):
        connection = redis.Redis(connection_pool=self.__pool)
        try:
            connection.delete(id)
        except Exception as e:
            print(e)
        finally:
            del connection


#########################################################################
### 持久化储存对话记录
#########################################################################

from pymongo import MongoClient
from bson.objectid import ObjectId


class MongoDb:
    def __init__(self, host, username, password):
        self.__client = MongoClient(host=host, port=27017)
        self.__client.admin.authenticate(username, password)

    def insert(self, question, answer):
        try:
            self.__client['bank_record']['conversation'].insert_one({"question": question,
                                                                    "answer": answer})
        except Exception as e:
            print(e)

    def search_id(self, question):
        try:
            news = self.__client['bank_record']['conversation'].find_one({"question": question})
            return str(news["_id"])
        except Exception as e:
            print(e)

    def update(self, id, question, answer):
        try:
            self.__client['bank_record']['conversation'].update_one({"_id": ObjectId(id)},
                                                   {"$set": {"question": question, "answer": answer}})
        except Exception as e:
            print(e)

    def search_answer_by_id(self, id):
        try:
            news = self.__client['bank_record']['conversation'].find_one({"_id": ObjectId(id)})
            return news["answer"]
        except Exception as e:
            print(e)

    def delete_by_id(self, id):
        try:
            self.__client['bank_record']['conversation'].delete_one({"_id": ObjectId(id)})
        except Exception as e:
            print(e)