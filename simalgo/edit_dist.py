#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   edit_dist.py
@Author  :   Racle
@Version :   1.0
@Desc    :   None
'''


def editDistDP(s1, s2):
    """编辑距离计算
    params：文本1，string
            文本2，string
    """
    m = len(s1.strip())
    n = len(s2.strip())
    # 创建一张表格记录所有子问题的答案
    dp = [[0 for x in range(n+1)] for x in range(m+1)]
    # 从上往下填充DP表格
    for i in range(m+1):
        for j in range(n+1):
            if i == 0 or j == 0:
                dp[i][j] = max(i, j)
            # 如果两个字符串结尾字母相同，距离不变
            elif s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            # 如果结尾字母不同，那我们就需要考虑三种情况，取最小的编辑距离
            # 替换，添加，删除
            else:
                dp[i][j] = 1 + min(dp[i-1][j-1], dp[i][j-1], dp[i-1][j])

    return dp[m][n]