#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   rule_grammer.py
@Author  :   Racle
@Version :   1.0
@Desc    :   None
'''

import random
from functools import reduce
import operator as op


question_grammer = """
start => hello | ask
hello => hello_w ,  | None
ask => ask_w | None
ov => ov_seg
sen => start ov tail
hello_w => 你好 | 您好 | 不好意思 | 请问 | 给我解释 | 介绍一下 | 想知道
ask_w => 怎么 | 如何
tail => , tail_w | None | None | None
tail_w => 谢谢 | 感谢
"""


def create_grammar(grammar_str, split='=>', line_split='\n'):
    grammar = {}
    for line in grammar_str.split(line_split):
        if not line.strip(): continue  # None > continue
        exp, stmt = line.split(split)
        grammar[exp.strip()] = [s.split() for s in stmt.split('|')]
    return grammar


def generate(gram, target):
    if target not in gram: return target  # terminal expression 终止条件
    expanded = [generate(gram, t) for t in random.choice(gram[target])]
    return ''.join([e for e in expanded if e != 'null'])


def generate_modified(rule, grammar):
    if rule in grammar:
        pattern = random.choice(grammar[rule])
        return reduce(op.add, [generate_modified(p, grammar) for p in pattern])
    else:
        return [rule]


def generate_n(gram, target, n):
    sens = []
    for i in range(n):
        sen = generate_modified('sen', create_grammar(gram, split='=>'))
        sens.append(sen)
    return sens

# grammar = create_grammar(question_grammer)

print(generate_n(question_grammer, 'sen', 5))