#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   nlp.py
@Author  :   Racle
@Version :   1.0
@Desc    :   None
'''

import os
import re

from pyltp import Segmentor
from pyltp import Postagger
from pyltp import Parser
from pyltp import NamedEntityRecognizer
from pyltp import SentenceSplitter

LTP_DATA_DIR = 'D:/ProgramData/nlp_package/ltp_v34'

class Ltp:
    "https://pyltp.readthedocs.io/zh_CN/latest/"
    def __init__(self, seg=True, pos=False, ner=False, parse=False,
                 seg_lexicon_path=None, pos_lexicon_path=None):
        cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
        pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')
        ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径
        par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型

        if seg:
            self.segmentor = Segmentor()               #分词
            if seg_lexicon_path:
                self.segmentor.load_with_lexicon(cws_model_path,
                                                 seg_lexicon_path)
            else:
                self.segmentor.load(cws_model_path)

        if pos:
            # 输入分词结果
            self.postagger = Postagger()               #词性标注
            self.postagger.load(pos_model_path)
            if pos_lexicon_path:
                self.postagger.load_with_lexicon(pos_model_path,
                                                 pos_lexicon_path)
            else:
                self.postagger.load(pos_model_path)

        if ner:
            # 输入分词和标注结果
            self.ner = NamedEntityRecognizer()  #命名主体识别
            self.ner.load(ner_model_path)

        if parse:
            # 输入分词和标注结果
            self.parser = Parser()                     #依存分析
            self.parser.load(par_model_path)

    def release(self):
        try:
            self.segmentor.release()
            self.postagger.release()
            self.ner.release()
            self.parser.release()
        except AttributeError:
            pass

    def __del__(self):
        self.release()


class ProcessText:
    @staticmethod
    def token(string):
        return re.findall(r'[\d|\w]+', string)

    @staticmethod
    def cut(string, cut_method):
        return cut_method(string)

    def filter_text(self, content, cut_method):
        "保留数字、字母和汉字。return -- 分词结果列表"
        content = self.token(str(content).lower().strip())
        content = ' '.join(content)
        content = ' '.join(self.cut(content, cut_method))
        return content

    def __call__(self, content, cut_method):
        return self.filter_text(content, cut_method)


def load_stop(pathes):
    """
    pathes: 停用词路径list
    """
    stopwords = []
    for path in pathes:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                stopwords.append(line.strip())

    return list(set(stopwords))

