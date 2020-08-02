#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   app.py
@Author  :   Racle
@Version :   1.0
@Desc    :   None
'''

from dialogue import DialogManager
from flask import Flask, render_template, request


app = Flask(__name__, static_folder='templates', static_url_path='')


# 因为在使用sklearn tf-idf模型使用时自定义了分词方法， pickle load时需要该方法在__main__空间中
def split_func(s): return s.split()


bot = DialogManager()


@app.route('/api/chat', methods=['GET'])
def chat():
    query = request.args.get('message')
    print(query)
    output = bot.get_answer(query)
    return output


@app.route('/')
def main():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)