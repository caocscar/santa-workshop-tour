# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 13:19:35 2019

@author: caoa
"""
import pandas as pd
import numpy as np
import os
from utils import cost_function, preference_cost
from collections import Counter

pd.options.display.max_rows = 20

wdir = 'data'
df = pd.read_csv(os.path.join(wdir,'family_data.csv'), index_col='family_id')
family_choices = df.values
choice_dict = {i:list(choices) for i,choices in enumerate(family_choices)}
family_size_dict = dict(zip(df.index,df['n_people']))
sort_order = ['n_people'] + [f'choice_{i}' for i in range(2)]
asc_list = [False] + [False]*(len(sort_order)-1)
df.sort_values(sort_order, ascending=asc_list, inplace=True)
df.reset_index(inplace=True)

#%%
def check_occupancy(ch, ymax=230):
    if daily[ch-1] + row.n_people <= ymax:
        daily[ch-1] += row.n_people
        return True
    else:
        return False

def check_occupancy2(ch, prev, ymax=250):
    if (daily[ch-1] + row.n_people <= ymax) & (daily[prev] - row.n_people >= 125):
        daily[ch-1] += row.n_people
        daily[prev] -= row.n_people
        return True
    else:
        return False
    
def assign_min_day():
    ch_ = np.argmin(daily)
    daily[ch_] += row.n_people
    return ch_    
    
#%% initial assignment
# progression
# [455,2650,2702,3161,3583,3583,3583,4012,4032,4032]
daily = np.zeros((100,1), dtype=np.int16)
index, result = [],[]
for k, row in enumerate(df.itertuples()):
    choices = [row.choice_0, row.choice_1, row.choice_2, row.choice_3, row.choice_4,
               row.choice_5, row.choice_6, row.choice_7, row.choice_8, row.choice_9,
               ]
    idx = 0
    ch = choices[idx]
    flag = False
    while not flag:
        flag = check_occupancy(ch)
        if flag:
            result.append((row.family_id, ch, row.n_people, idx, preference_cost(idx,row.n_people)))
            index.append(idx)
        else:
            idx += 1
            if idx > 9:
                min_idx = assign_min_day()
                result.append((row.family_id, min_idx+1, row.n_people, idx, preference_cost(idx,row.n_people)))
                index.append(10)
                flag = True
            else:
                ch = choices[idx]

f = pd.DataFrame(result, columns=['family_id','day','n','ch','pc'])
f.sort_values('family_id', inplace=True)
assign_day = f['day'].to_list()
c = Counter(index)
pen = f[f['ch'] > 0]
pen.sort_values(['pc','ch'], ascending=False, inplace=True)
pen = pen.merge(df, how='inner', on='family_id')

#%%
score, pcost, acost, daily_double, pc, ap = cost_function(assign_day, family_size_dict, choice_dict)
print(f'Score = {score[0]:,.0f}')
above = np.where(daily_double > 300,1,0).sum()
below = np.where(daily_double < 125,1,0).sum()
print(f'Above 300: {above} - max: {np.max(daily_double)}')
print(f'Below 125: {below} - min: {np.min(daily_double)}')
f.set_index('family_id', inplace=True)
submission = f[['day']].copy()
submission.columns = ['assigned_day']
assert submission.shape[0] == 5000
submission.to_csv('submission.csv')
    
