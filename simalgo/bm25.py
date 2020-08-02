#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   bm25.py
@Author  :   Racle
@Version :   1.0
@Desc    :   None
'''

from collections import Counter
from math import log


def get_tf(doc_i, sent_j):
    """计算bm25的term frequence. sent来自预处理的sent_of_words列表。"""
    freq = {}
    sent_i_counts = Counter(doc_i)
    # 计算i句中的词，在j句中的tf
    for w in sent_j:
        # if not self.filte_words(w_item):
        #     continue
        if w in sent_i_counts:
            freq[w] = sent_i_counts[w]
        else:
            freq[w] = 0
    total = len(doc_i)
    return {word: count / total for word, count in freq.items()}


def get_idf(content):
    """计算inverse document frequence"""
    total_sent = len(content) + 1 # 假设有一个句子包含所有词
    avg_len = 0
    doc_freq = {}
    for sent in content:
        sent = sent.lower().split()
        avg_len += len(sent)
        words = list({w for w in sent})
        for word in words:
            # 假设有一个句子包含所有词
            count = doc_freq.setdefault(word, 1)
            doc_freq[word] = count + 1
    avg_len /= total_sent
    # sklearn中的实现方式
    idf = {word: log(total_sent / df) + 1 for word, df in doc_freq.items()}
    return idf, avg_len


def sent_corelation_func(doc_i, sent_j, idf, avg_len, k1=1.5, b=0.75):
    """计算bm25。

    doc_i ： 与query对比的对象，在候选集中进行遍历，D
    sent_j : query的句子, Q
    """
    tf = get_tf(doc_i, sent_j)

    K = k1 * (1 - b + b * len(doc_i) / avg_len)
    bm25 = 0
    for j_word in sent_j:
        try:
            bm25 += idf[j_word] * tf[j_word] * (k1 + 1) / (tf[j_word] + K)
        except KeyError:
            continue

    return bm25