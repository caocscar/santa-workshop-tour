# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 13:33:53 2019

@author: caoa
"""
import numpy as np

def preference_cost(choice, n):
    cost_dict = {0: 0,
                 1: 50,
                 2: 50 + 9*n,
                 3: 100 + 9*n,
                 4: 200 + 9*n,
                 5: 200 + 18*n,
                 6: 300 + 18*n,
                 7: 300 + 36*n,
                 8: 400 + 36*n,
                 9: 500 + 36*n + 199*n,
    }
    return cost_dict.get(choice, 500 + 36*n + 398*n)

def accounting_cost(daily_occupancy,days):
    accounting_penalty = (daily_occupancy[days[0]]-125.0) / 400.0 * daily_occupancy[days[0]]**(0.5)
    # using the max function because the soft constraints might allow occupancy to dip below 125
    accounting_penalty = max(0, accounting_penalty)
    ap = []
    
    # Loop over the rest of the days, keeping track of previous count
    yesterday_count = daily_occupancy[days[0]]
    for day in days[1:]:
        today_count = daily_occupancy[day]
        diff = abs(today_count - yesterday_count)
        daily_cost = max(0, (daily_occupancy[day]-125.0) / 400.0 * daily_occupancy[day]**(0.5 + diff / 50.0))
        accounting_penalty += daily_cost
        ap.append(daily_cost[0])
        yesterday_count = today_count
    
    return accounting_penalty, ap
    
def cost_function(prediction, family_size_dict, choice_dict):

    score = 0
    days = list(reversed(range(100)))
    daily_occupancy = np.zeros((100,1), dtype=np.int16)
    
    pcost = 0
    pc = []
    for family_id, day in enumerate(prediction):
        n = family_size_dict[family_id]
        try:
            choice = choice_dict[family_id].index(day)
        except ValueError:
            choice = 77
        pc.append(preference_cost(choice,n))
        pcost += pc[-1]
        # add the family member count to the daily occupancy
        daily_occupancy[day-1] += n

    #  (using soft constraints instead of hard constraints)
    pmin = np.min(daily_occupancy)
    pmax = np.max(daily_occupancy)
    if (pmax > 300) or (pmin < 125):
        print('OUTER LIMITS')
        score += 100000000

    # Calculate the accounting cost
    apenalty, ap = accounting_cost(daily_occupancy, days)
    score += pcost + apenalty

    return score, pcost, apenalty, daily_occupancy.T, pc, reversed(ap)
