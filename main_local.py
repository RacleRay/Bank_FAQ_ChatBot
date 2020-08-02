#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Author  :   Racle
@Version :   1.0
@Desc    :   None
'''

from dialogue import DialogManager


# 因为在使用sklearn tf-idf模型使用时自定义了分词方法， pickle load时需要该方法在__main__空间中
def split_func(s): return s.split()


def main():
    bot = DialogManager()

    while True:
        query = input('>>>:')
        answer = bot.get_answer(query)
        print('Bot: ', answer)


if __name__ == '__main__':
    main()