#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   searcher.py
@Author  :   Racle
@Version :   1.0
@Desc    :   None
'''

import pandas as pd
from operator import and_
from functools import reduce
from functools import partial

import nlp
from simalgo import bm25, edit_dist
from utils import (
    unpickle_file,
    distance,
    load_annoy_index,
    load_gensim_vec,
    sent_avg_vec,
    PrioritizedItem,
    KLargest
)
from corrector import Corrector


filter_allowed_pos = {'n', 'v', 'm', 'nh', 'ni', 'nl', 'ns', 'nt', 'ws'}
filter_allowed_pos_n = {'n', 'nh', 'ni', 'nl', 'ns', 'ws'}


class Retrival:
    def __init__(self, datapath,):
        print('Initializing retrival model...')
        self.data = pd.read_csv(datapath)
        self.tfidf = unpickle_file('model/tfidf.model')

        self.tfidf_vec = unpickle_file('data/doc_tfidf_vec.bin')
        self.inverse_idx = unpickle_file('data/inverse_idx_table.bin')

        self.word_2_id = unpickle_file('data/full_word2id.bin')
        self.id_2_word = {d: w for w, d in self.word_2_id.items()}
        self.word_2_id_for_filter = unpickle_file('data/tfidf_word2vec.bin')
        self.idf, self.avg_len = unpickle_file('data/idf_and_avglen.bin')

        self.word_vec = load_gensim_vec('data/wordvec_fasttext_300.txt')
        self.annoy = load_annoy_index('data/sentvec.ann')

        self.ltp = nlp.Ltp(seg=True, pos=True,
                           seg_lexicon_path='data/lexicon_seg.txt',
                           pos_lexicon_path='data/lexicon.txt')
        self.text_precess = nlp.ProcessText()

        self.stopwords = nlp.load_stop(['data/chinese_stopwords.txt', 'data/哈工大停用词表.txt'])
        self.nonsense_word = ['请问', '想知道']

        self.corrector = Corrector()
        print('Retrival model established.')

    def input_query(self, query):
        """用户输入query处理。

        return:
            布尔搜索是否有结果 -- boolen。假如为False，将不进行除word2vec外的召回方法
        """
        boolen_res_idx, words, to_correct, allowed = self._deal_query(query, filter_allowed_pos, do_correct=True)

        if len(boolen_res_idx) == 0:
            # 进行文本纠错
            # Note: 限制词性减小搜索空间，但是纠错的效果就与分词和词性标注的效果关系很大了，有利有弊
            #       不限制词性，N-Gram贪心法排列纠错，计算量依然会比较大。还是选择尽量较小计算量的方法。
            query, words_corrected = self.corrector(query, to_correct)
            boolen_res_idx, words, _, allowed = self._deal_query(query, filter_allowed_pos, do_correct=False)
        if len(boolen_res_idx) == 0:
            # 放宽词性搜索条件
            boolen_res_idx, words, _, allowed = self._deal_query(query, filter_allowed_pos_n, do_correct=False)

        self.query = query
        self.boolen_res_idx = boolen_res_idx
        self.words = words
        self.allowed_words = allowed

        return False if len(boolen_res_idx) == 0 else True

    def _deal_query(self, query, filter_allowed_pos, do_correct=True):
        """
        return:
            boolen_res_idx -- 布尔搜索结果id list
            words -- 文本处理后的词 str
            to_correct -- 文本纠错目标 list
            allowed -- 词性过滤之后的词 list
        """
        words = self.text_precess(query, self.ltp.segmentor.segment)
        candidates_ids, to_correct, allowed = self.filter_pos(words,
                                                              filter_allowed_pos,
                                                              correct=do_correct)
        boolen_res_idx = {}
        # 因为filter_pos函数中忽略了潜在错误的词汇，所以需要判定是否相等
        if len(candidates_ids) == len(allowed):
            # 布尔搜索：找到同时包含关键词的文档
            documents_ids = [self.inverse_idx[_id] for _id in candidates_ids]
            if len(documents_ids) > 0:
                boolen_res_idx = reduce(and_, documents_ids)

        return boolen_res_idx, words, to_correct, allowed

    def search_tfidf(self, top_k=10):
        """对query进行： pos filter -> inverse idx search -> boolen search -> similarity ranking
        获取召回模块筛选的词汇.
        """
        if len(self.boolen_res_idx) == 0:
            return []
        # 计算相似性排序
        query_vec = self.tfidf.transform([self.words]).toarray()

        k_largest_heap = KLargest(top_k)  # 堆为小顶堆，注意使用负的distance
        for i in self.boolen_res_idx:
            k_largest_heap.add(
                (PrioritizedItem(-distance(query_vec, self.tfidf_vec[i].toarray()), i))
            )
        # 只对前十的元素排序
        sorted_docuemtns_id = [i.item for i in sorted(k_largest_heap.pool, reverse=True)]
        return sorted_docuemtns_id

    def search_bm25(self, top_k=10):
        "bm25计算得分，进行召回"
        if len(self.boolen_res_idx) == 0:
            return []

        f = partial(bm25.sent_corelation_func,
                    sent_j=self.words.split(),
                    idf=self.idf,
                    avg_len=self.avg_len)

        k_largest_heap = KLargest(top_k)  # 堆为小顶堆，得分用正值
        for i in self.boolen_res_idx:
            k_largest_heap.add(
                (PrioritizedItem(f(self.data.q_processed[i].split()), i))
            )
        # 只对前十的元素排序
        sorted_docuemtns_id = [i.item for i in sorted(k_largest_heap.pool, reverse=True)]

        return sorted_docuemtns_id

    def search_editdist(self, top_k=10):
        "编辑距离"
        if len(self.boolen_res_idx) == 0:
            return []

        f = partial(edit_dist.editDistDP, self.query.lower().strip())

        k_largest_heap = KLargest(top_k)  # 堆为小顶堆，使用负的distance
        for i in self.boolen_res_idx:
            k_largest_heap.add(
                (PrioritizedItem(-f(self.data.question[i].lower()), i))
            )
        # 只对前十的元素排序
        sorted_docuemtns_id = [i.item for i in sorted(k_largest_heap.pool, reverse=True)]

        return sorted_docuemtns_id

    def search_fasttext(self, top_k=20, include_distances=False):
        """使用fasttext在wiki上预训练的模型，然后在任务数据上fine tuning, 得到词向量。
        只提取出任务包含的词向量部分，在此召回场景下已经足够，并且提升了性能。
        """
        q_vec = sent_avg_vec(self.words, self.word_vec)
        if q_vec is None:
            return []
        sorted_docuemtns_id = self.annoy.get_nns_by_vector(q_vec,
                                                top_k,
                                                search_k=-1,
                                                include_distances=include_distances)
        return sorted_docuemtns_id

    def __search_simhash(self, query):
        "simhash相对而言更适用于较长文本，此处没有使用，可以在simalgo文件夹下导入使用"
        from simalgo.simhash import Simhash, SimhashIndex

        # 这部分hashed_objs应该先计算保存，此处直接使用，只做演示，因为实际没有用到该算法
        hashed_objs = [(str(v.qid), Simhash(str(v.question)))
                        for k, v in self.data[['qid', 'question']]]

        # 建立SimhashIndex对象，`k` is the tolerance, bit位相差数量限制
        index = SimhashIndex(hashed_objs, k=10)
        # print("相似文本Bucket数量：", index.bucket_size())

        q_hash = Simhash(query)

        sorted_docuemtns_id = sorted(index.get_near_dups(q_hash),
                                    lambda x: x[1])

        return sorted_docuemtns_id

    def filter_pos(self, words, pos_allowed, correct=False):
        "根据pos，过滤进入boolen search的word。correct为True时，输出需要关注的待纠正词"
        words = words.split()
        postags = self.ltp.postagger.postag(words)

        allowed = []
        to_correct = []
        if correct:
            pre_tag = "@"
            pre_word = ""
            for i, postag in enumerate(postags):
                cur_word = words[i]
                if cur_word in self.nonsense_word:
                    continue
                # 后缀处理: pre_tag == 'n', 那么一定在to_correct中
                if pre_tag == 'n' and len(pre_word) <= 2 and postag in ['a', 'k', 'n'] and len(cur_word) == 1:
                    to_correct[-1] = to_correct[-1] + cur_word
                elif postag in pos_allowed:
                    allowed.append(cur_word)
                    # 前缀处理: pre_tag的词没有出现在to_correct中
                    if pre_tag in ['a', 'h'] and len(pre_tag) == 1 and len(cur_word) <= 2:
                        to_correct.append(pre_word + cur_word)
                    else:
                        to_correct.append(cur_word)
                pre_tag = postag
                pre_word = cur_word
        else:
            for i, postag in enumerate(postags):
                cur_word = words[i]
                if cur_word in self.nonsense_word:
                    continue
                if postag in pos_allowed:
                    allowed.append(cur_word)

        candidates_ids = []
        for w in allowed:
            try:
                candidates_ids.append(self.word_2_id_for_filter[w])
            except KeyError:
                pass

        return candidates_ids, to_correct, allowed