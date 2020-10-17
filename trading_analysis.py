# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 16:38:01 2020

@author: r0772291
根据交易序列，计算收益
"""
import os
import datetime
import quantstats as qs
import pandas as pd
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client["JointQuant"]
path = 'E:\\trailing\\'
fileList = os.listdir(path)
for onefile in fileList:
    if onefile[-3:] == 'csv':
        fileList.remove(onefile)
for onefile in fileList:
    cash = 100000
    position = 0
    code = onefile.split('_')[0]
    print ('================',code, '==========================')
    df1 = pd.read_csv(path+onefile+'\\Test_1\\'+'memory_1.csv')
    df2 = df1[['date', 'position', 'action']]
    df3 = df2.set_index('date')
    
    startDate = df3.index[0]
    df0 = pd.DataFrame(list(db[code].find().sort('date'))).set_index('date')
    df0 = df0[['close']]
    price_df = df0.loc[startDate:]
    
    df_all = price_df.join(df3, how='outer')
    
    allValue = []
    for i in range(len(df_all)):
        if df_all.iloc[i]['action'] == 1: #买入
            if position == 0:
                '''
                position = cash//(df_all.iloc[i]['position']*100) # 买入的股票数量
                cash = cash%(df_all.iloc[i]['position']*100)
                allValue.append(cash + df_all.iloc[i]['position']*100*position)
                '''
                position = cash//(df_all.iloc[i]['close']*100) # 买入的股票数量
                cash = cash%(df_all.iloc[i]['close']*100)
                allValue.append(cash + df_all.iloc[i]['close']*100*position)
            elif position > 0:
                allValue.append(cash + df_all.iloc[i]['close']*100*position)
        elif df_all.iloc[i]['action'] == -1: #卖出
            if position > 0:
                #cash = cash + df_all.iloc[i]['position']*position*100
                cash = cash + df_all.iloc[i]['close']*position*100
                position = 0
                allValue.append(cash)
            elif position == 0:
                cash = cash + df_all.iloc[i]['close']*position*100
                allValue.append(cash)
        else:
          value0 = cash + position*df_all.iloc[i]['close']*100
          allValue.append(value0)
    df_all['allReturn'] = allValue
    
    AP = df_all['allReturn'].values[-1]-df_all['allReturn'].values[0]
    SR = qs.stats.sharpe(df_all['allReturn'])
      
    # 计算最大回撤
    max_return = max(allValue)
    index_ = list(allValue).index(max_return)
    min_return = min(allValue[index_:])
    MDD = (min_return-max_return)/max_return
     
    df_all.to_csv(path + code + '_eachday_return.csv')    
    df_all.index = [datetime.datetime.strptime(one, '%Y-%m-%d') for one in df_all.index]
    print ('calmar is ', qs.stats.calmar(df_all['allReturn']))
    print (qs.reports.metrics(df_all['allReturn']))   