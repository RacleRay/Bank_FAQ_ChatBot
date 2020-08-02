#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   tracker.py
@Author  :   Racle
@Version :   1.0
@Desc    :   None
'''

import kenlm
from patterns import rules
from utils import find_word


class Tracker:
    def __init__(self):
        self.previous_cache = None
        self.load_lm()

    def check(self, query):
        "当前输入符合定义的某些模式"
        query = find_word(query)
        for rule in rules:
            q_pattern_match = pattern_pos_match(rule, query)
            if q_pattern_match[0][0]:
                self.keyword = ''.join(q_pattern_match[0][1])
                return True
        return False

    def fill_query(self):
        "替换在query中关键词，通过语言模型确定可能的最优question"
        if not self.previous_cache or not self.previous_cache[1]:
            return None

        pre_query = self.previous_cache[0]
        pre_keywords = self.previous_cache[1]

        best_q = ''
        best_score = -10000
        for w in pre_keywords:
            candi_q = pre_query.replace(w, self.keyword)
            score = self.lm.score(self.space_split(candi_q))
            if score > best_score:
                best_score = score
                best_q = candi_q

        return best_q

    def load_lm(self, path="./model/lm.bin"):
        self.lm = kenlm.LanguageModel(path)

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


symbol = {'?*y', '?*x', '?*z', '?x', '?y', '?z'}
fail = [(False, False)]


def place_holder_split(pattern):
    "处理symbol划分问题. 此处没有使用，在定义rule时，已经处理"
    pre = '@'
    line = ''
    count = 0
    for s in pattern:
        if ord('A') <= ord(pre) <= ord('z') and ord('A') <= ord(s) <= ord('z'):
            line += s
        elif (pre == '?' and (s == '*' or s in 'xyz')) or (pre == '*' and s in 'xyz'):
            line += s
            if s in 'xyz':
                count += 1
        else:
            line += ' ' + s
        pre = s
    return line.split(), count


def pattern_pos_match(pattern, query):
    """匹配?*, ?对应位置

    return:
        [(symbol, target words), (symbol, target words)]
    """
    if not pattern or not query: return []  # 空

    candidate_p = pattern[0]
    # 匹配一个词
    if candidate_p in {'?x', '?y', '?z'}:
        return [(candidate_p, query[0])] + pattern_pos_match(pattern[1:], query[1:])
    # 匹配多个词
    elif candidate_p in {'?*x', '?*y', '?*z'}:
        match, index = multi_match(pattern, query)
        if match:
            return [match] + pattern_pos_match(pattern[1:], query[index:])
        else:
            return fail
    # 相同继续
    elif candidate_p == query[0]:
        return pattern_pos_match(pattern[1:], query[1:])
    else:
        return fail


def multi_match(pattern, query):
    """对匹配的第一个部分，进行提取

    return:
        匹配对应元组 (symbol, words)
        下一次搜索起点 index
    """
    first_pos, rest = pattern[0], pattern[1:]
    first_pos = first_pos.replace('?*', '?')
    # 没有rest项，直接匹配query全部
    if not rest: return (first_pos, query), len(query)

    # 找到匹配符对应的部分
    for i, token in enumerate(query):
        # rest[0]：不是symbol的第一个字符
        if rest[0] == token and is_match(rest[1:], query[(i + 1):]):
            return (first_pos, query[:i]), i

    return None, None


def is_match(rest, query):
    "判断剩余部分的匹配情况，这是有必要的（当匹配模式中有多个与rest[0]相同）"
    # 空
    if not rest and not query:
        return True
    # 匹配到匹配符
    if rest[0] in symbol:
        if len(rest) == 1:
            return True
        else:
            return is_match(rest[1:], query)
    # 不匹配
    if rest[0] != query[0]:
        return False
    else:
        return is_match(rest[1:], query[1:])


def format_result(match_result):
    "格式化匹配结果"
    return {k: ''.join(v) if isinstance(v, list) else v for k, v in match_result}