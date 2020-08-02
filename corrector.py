#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   corrector.py
@Author  :   Racle
@Version :   1.0
@Desc    :   None
'''

import string
import datrie
import kenlm

from itertools import product
from pypinyin import lazy_pinyin

from utils import unpickle_file


class Corrector:
    def __init__(self, ):
        print('Initializing corrector model...')
        self.trie = unpickle_file('model/correct_datrie.bin')
        self.word_frequence = unpickle_file('data/word_frequence.bin')
        self.load_lm()
        self.vocabulary = unpickle_file('data/vocabulary.bin')
        print('Corrector model established.')

    def correct_query(self, query, to_correct):
        """基于modified Kneser-Ney smoothing的语言模型，使用double array trie，进行简单文本纠错
        相比于目前的bert based方法，更轻量，更可控，更快速。适用于在线即时纠错。缺点在于不够灵活，
        需要设计的部分更多。

        query： -- 用户输入的query
        to_correct： -- 识别出的待验证词组list
        """
        start_idx = 0
        words_corrected = []
        for word in to_correct:
            if word in self.vocabulary:
                continue
            idx = query.index(word, start_idx)
            best_lm_score = -10000

            if self.check_english(word):  # 英文直接找
                possibles = self.frequence_filter(self.find_candidates(word))
            else:
                possible_w = []
                for w in word:  # 汉语一个字一个字替换
                    filter_words = self.frequence_filter(self.find_candidates(w))
                    possible_w.append(filter_words)
                possibles = product(*possible_w)

            # 贪心法求解纠错结果。全量搜索空间太大，复杂度指数级增长。经过词频筛选，约束复杂度。
            candi = ''
            for repl in possibles:
                tmp = query[: start_idx] + query[start_idx: ].replace(word, ''.join(repl), 1)
                score = self.lm.score(self.space_split(tmp))
                if score > best_lm_score:
                    best_lm_score = score
                    candi = tmp
            query = candi
            words_corrected.append(query[idx: idx + len(word)])

            start_idx = idx + len(word)

        return query, words_corrected

    def load_lm(self, path="./model/lm.bin"):
        self.lm = kenlm.LanguageModel(path)

    def __call__(self, query, to_correct):
        return self.correct_query(query, to_correct)

    def find_candidates(self, w):
        candidates = set()
        pin = lazy_pinyin(w)[0]
        try:
            # prefix查找
            not_leaf = list(filter(lambda x: 0 <= (len(pin) - len(x)) <= 1, self.trie.prefixes(pin)))

            if len(not_leaf) == 0:
                not_leaf = self.trie.prefixes(pin)[0]

            for prefix in not_leaf:
                suffixes = self.trie.suffixes(prefix)
                for suf in suffixes:
                    cand = prefix + suf
                    # 长度限制
                    if 0 <= abs(len(cand) - len(pin)) <= 1:
                        candidates.add(self.trie[cand])

            candidates.add(w)
        except KeyError:
            pass
        return candidates

    def frequence_filter(self, possible_set):
        return sorted(list(possible_set),
                      key=lambda w: self.word_frequence.get(w, 0),
                      reverse=True)[:5]

    @staticmethod
    def space_split(strings):
        "空格分隔字符，处理为KenLM输入格式"
        pre = '@'
        line = ''
        for s in strings:
            if ord('A') <= ord(pre) <= ord('z') and ord('A') <= ord(s) <= ord('z'):
                line += s
            else:
                line += ' ' + s
            pre = s
        return line

    @staticmethod
    def check_english(w):
        "对于这种分过词的数据，直接简单判定"
        return (ord('a') <= ord(w[0]) <= ord('z')) and ((ord('a') <= ord(w[-1]) <= ord('z')))

    @staticmethod
    def build_trie(words_pin_dict):
        trie = datrie.Trie(string.ascii_lowercase + string.digits)

        for w, pin in words_pin_dict.items():
            if pin in trie and w == trie[pin]:
                continue
            # 相同拼音处理
            if pin in trie and w != trie[pin]:
                i = 1
                flag = True
                while flag:
                    key = pin + str(i)
                    if key not in trie:
                        flag = False
                    i += 1
                trie[key] = w
            else:
                trie[pin] = w

        return trie