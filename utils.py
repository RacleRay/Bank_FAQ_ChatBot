#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   utils.py
@Author  :   Racle
@Version :   1.0
@Desc    :   None
'''
import re
import pickle
import string
import heapq
import numpy as np
from annoy import AnnoyIndex
from gensim.models import KeyedVectors
from scipy.spatial.distance import cosine


def array_to_string(arr):
    return ' '.join([str(i) for i in arr])


def find_word(s):
    pattern = re.compile(r'[\u4e00-\u9fa5]|[abcdefghijklmnopqrstuvwxyz]+')
    return re.findall(pattern, s.lower())


def simple_process(s):
    return s.lower().strip()


def sent_avg_vec(sent, word_vec, idf=None):
    "idf -- 可选择使用idf reweighting"
    res = 0
    length = 0
    if idf: default = min(idf.values()) - 0.5
    if isinstance(sent, str): sent = sent.split()
    for w in sent:
        try:
            factor = 1 if idf is None else idf.get(w, default)
            res += factor * word_vec.get_vector(w)
            length += 1
        except KeyError:
            continue
    # maybe divide by zero
    return res / length if length > 0 else None


def get_wordvec_dict(sents, word_vec, idf=None):
    vec_ = []
    for sent in sents:
        if isinstance(sent, str):
            sent = sent.split()
        try:
            vec = sent_avg_vec(sent, word_vec, idf)
        except ZeroDivisionError:
            vec = np.zeros((300,))
        vec_.append(vec)
    return vec_


def distance(v1, v2): return cosine(v1, v2)


def save_pickle(path, data):
    # pickle不能保存lambda
    fileObject = open(path, 'wb')
    pickle.dump(data, fileObject)
    fileObject.close()


def unpickle_file(filename):
    """Returns the result of unpickling the file content."""
    with open(filename, 'rb') as f:
        return pickle.load(f)


def build_inverse_idx_table(doc_word):
    "此处输入为数据集 sklearn 进行 tfidf fit_transform 的结果"
    inverse_data = doc_word.transpose()
    inverse_idx = []
    for arr in inverse_data:
        inverse_idx.append(set(np.nonzero(arr.toarray()[0])[0]))
    return inverse_idx


def build_annoy_index(vec_list, savepath, dim=300, metric='angular', n_trees=10):
    index = AnnoyIndex(dim, metric)

    for i, vec in enumerate(vec_list):
        index.add_item(i, vec)
    index.build(n_trees)

    index.save(savepath)
    return index


def load_annoy_index(path, dim=300, metric='angular'):
    index = AnnoyIndex(dim, metric)
    index.load(path)
    return index


def load_gensim_vec(path):
    word_vectors = KeyedVectors.load_word2vec_format(path)
    return word_vectors


# =========== Heap =============
from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any=field(compare=False)


class KLargest:
    def __init__(self, k: int, nums=[]):
        self.pool = heapq.nlargest(k, nums)
        heapq.heapify(self.pool)
        self.k = k

    def add(self, val):
        if len(self.pool) < self.k:
            heapq.heappush(self.pool, val)
        else:
            heapq.heappushpop(self.pool, val)