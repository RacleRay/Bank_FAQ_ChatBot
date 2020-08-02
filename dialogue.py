#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   dialogue.py
@Author  :   Racle
@Version :   1.0
@Desc    :   None
'''

from searcher import Retrival
from ranker import Ranker
from tracker import Tracker

from utils import simple_process


class DialogManager:
    def __init__(self):
        print('Loading dialog manager...')

        self.retriever = Retrival('data/qa_processed')
        self.ranker = Ranker('localhost')

        # self.ANSWER_TEMPLATE = "您可能想问：%s\n最佳答案：%s \n distance: %f"  # debug
        self.ANSWER_TEMPLATE = "您是说：“%s” 吗？  Friday想了想：%s"

        # simple_state_tracker
        self.tracker = Tracker()

        self.threshold = 0.02  # 问题是否不确定的阈值

        self.spider = None  # TODO
        print('DialogManager established.')

    def get_answer(self, query):
        # 输入query，进行文本处理和布尔搜索
        query = simple_process(query)
        bool_state = self.retriever.input_query(query)
        query = self.retriever.query  # 可能进行了文本纠错

        # 检测最近一次对话，处理信息缺失情况. e.g. “那xx呢?”
        if self.tracker.check(query):
            tmp = self.tracker.fill_query()
            if len(tmp) > 0:
                query = tmp
                bool_state = self.retriever.input_query(query)

        # 对召回的结果进行更进一步的排序
        candi_idx, candi_q = self.recall_candidates(bool_state)
        if len(candi_idx) == 0:
            if len(self.allowed_words) == 0:
                return '非常抱歉，我不明白您的意思'
            else:
                return '非常抱歉，我不明白您的意思。你可以问问其他关于“{}”的问题'.format(
                    ' '.join(self.allowed_words))
        results = self.ranker.rank(query, candi_idx, candi_q, top=1) # (q_id, distance)

        # 读取结果
        best_match = self.retriever.data.iloc[results[0][0]].question
        answer = self.retriever.data.iloc[results[0][0]].answer
        distance = results[0][1]
        # 保存最近一次对话
        filted_words = self.retriever.allowed_words
        self.tracker.previous_cache = (query, filted_words)

        if distance < self.threshold:
            return str(answer)
        else:
            return self.ANSWER_TEMPLATE % (best_match, answer)

        # for debug
        # return self.ANSWER_TEMPLATE % (best_match, answer, distance)


    def recall_candidates(self, bool_state):
        result_candidates = set()
        # 处理当布尔搜索没有结果的情况。在input_query时，已经通过文本纠错和放宽约束
        # 只进行词向量搜索。
        if bool_state == True:
            result_candidates.update(self.retriever.search_tfidf(top_k=10))
            result_candidates.update(self.retriever.search_bm25(top_k=10))
            result_candidates.update(self.retriever.search_editdist(top_k=10))
            result_candidates.update(self.retriever.search_fasttext(top_k=10))
        else:
            result_candidates.update(self.retriever.search_fasttext(top_k=20))

        candi_idx = list(result_candidates)
        candi_q = []
        for idx in result_candidates:
            candi_q.append(self.retriever.data.iloc[idx].question)

        return candi_idx, candi_q

    def eval(self, query, topn=10):
        # 输入query，进行文本处理和布尔搜索
        query = simple_process(query)
        bool_state = self.retriever.input_query(query)

        # 检测最近一次对话，处理信息缺失情况. e.g. “那xx呢?”
        cur_words = self.retriever.words
        if self.tracker.check(cur_words):
            query = self.tracker.fill_query(cur_words)
            bool_state = self.retriever.input_query(query)

        # 对召回的结果进行更进一步的排序
        candi_idx, candi_q = self.recall_candidates(bool_state)
        if len(candi_idx) == 0:
            return ['非常抱歉，我不明白您的意思' for i in range(topn)]
        results = self.ranker.rank(query, candi_idx, candi_q, top=topn) # (q_id, distance)
        q_list = []
        for idx, _ in results:
            q_list.append(self.retriever.data.iloc[idx].question)

        # 保存最近一次对话
        filted_words = self.retriever.allowed_words
        self.tracker.previous_cache = (query, filted_words)

        return q_list