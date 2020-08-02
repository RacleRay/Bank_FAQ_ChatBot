#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   eval.py
@Author  :   Racle
@Version :   1.0
@Desc    :   None
'''

import pandas as pd
from dialogue import DialogManager


def eval():
    topn = 10
    data = pd.read_csv('data/qa_processed')
    questions = data.sample(100)['question'].tolist()

    bot = DialogManager()
    result_df = {'top' + str(i): [] for i in range(topn)}
    for question in questions:
        cand_questions = bot.eval(question, topn=topn)
        for i, q in enumerate(cand_questions):
            result_df['top' + str(i)].append(q)

    result_df['input'] = questions
    result_df['model'] = ['my_model' for i in range(len(questions))]

    eval_data = pd.DataFrame(result_df)
    eval_data.to_csv('./data/eval_data.csv')

    print('finished create eval data')


# 因为
def split_func(s): return s.split()


if __name__ == '__main__':
    eval()