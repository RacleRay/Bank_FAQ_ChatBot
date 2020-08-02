#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ranker.py
@Author  :   Racle
@Version :   1.0
@Desc    :   None
'''

from bert_serving.client import BertClient
from utils import distance


class Ranker:
    def __init__(self, ip='localhost', port=5555, port_out=5556):
        print('Initializing ranker...')
        self.bc = BertClient(ip, port, port_out)
        print('Ranker established.')

    def rank(self, query, candi_idx, candi_q, top=10):
        """抽取bert倒数第二层的每一步的hidden output，进行reduce mean生成sentence表示。
        由于没有标准数据，直接采用向量表示之间的距离来rank.

        query -- string
        candi_idx -- retrieval result id list
        candi_q -- retrieval result q content list

        return:
            top k的 (q_id, distance) rank结果
        """
        candi_q.insert(0, query)
        sentences = candi_q
        query_embedding, candi_embedding = self.get_represent(sentences)
        distances = [distance(query_embedding, embd) for embd in candi_embedding]
        return sorted(zip(candi_idx, distances), key=lambda x: x[1])[:top]

    def get_represent(self, sentences):
        "sentences将query与候选candidates联合输入bert，提升计算效率"
        encode_res = self.bc.encode(sentences)
        query_embedding = encode_res[0]
        candi_embedding = encode_res[1: ]
        return query_embedding, candi_embedding