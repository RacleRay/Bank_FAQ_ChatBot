#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:Raclerrr
# datetime:2019/7/17 13:09
# software:PyCharm
# modulename:pattern_match_chatbot


import random
from rules import rule_responses


# 这是对一些模式问题，进行回复的pattern match方法。可以加入到主模型中。
# 但是设计pattern，需要根据实际情况，作为模型的一种补充。

fail = [(False, False)]
def pattern_pos_match(pattern, query):
    "匹配?*, ?对应位置"
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


def substitute(pattern, pats_dict):
    "将用于回答的pattern，利用问句pattern解析的结果，进行处理"
    if not pattern: return []  # 没有答句pattern
    # 从pat_dict中get到pattern，没有就返回自身
    return [pats_dict.get(pattern[0], pattern[0])] \
            + substitute(pattern[1:], pats_dict)


def space_split(strings):
    "空格分隔字符"
    pre = '@'
    line = ''
    for s in strings:
        if ord('A') <= ord(pre) <= ord('z') and ord('A') <= ord(s) <= ord('z'):
            line += s
        else:
            line += ' ' + s
        pre = s
    return line.split()


def place_holder_split(pattern):
    "处理symbol划分问题"
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


def format_result(match_result):
    "格式化匹配结果"
    return {k: ''.join(v) if isinstance(v, list) else v for k, v in match_result}


def get_response(query, response_rules):
    '获取匹配回答'
    query = space_split(query.lower().strip())

    for q_pattern, a_pattern in response_rules.items():
        q_pattern_split, count = place_holder_split(q_pattern)
        q_pattern_match = pattern_pos_match(q_pattern_split, query)
        # print(q_pattern_match)
        if q_pattern_match[0][0]:
            q_pattern_match_dict = format_result(q_pattern_match)
            a_pattern_split, _ = place_holder_split(random.choice(a_pattern))
            answer = substitute(a_pattern_split, q_pattern_match_dict)
            return answer

    return '我不明白你在说什么'


if __name__=='__main__':
    symbol = {'?*y', '?*x', '?*z', '?x', '?y', '?z'}

    anwser = get_response('小明我很难过，因为很饿', rule_responses)
    print(anwser)