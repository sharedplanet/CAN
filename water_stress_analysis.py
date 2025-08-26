#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 16:32:57 2025

@author: manickamvalliappan
"""
import pandas as pd

df = pd.read_csv('all_hydrogen.csv')

hydrogen_df = df[df['Hydrogen production'] == True]

high_water_stress = [-1, 3, 4]

def compute_capacity_metrics(df_subset):
    total_capacity = df_subset['Capacity (MW)'].sum()
    high_ws_capacity = df_subset[df_subset['bws_cat'].isin(high_water_stress)]['Capacity (MW)'].sum()
    pct_high_ws = (high_ws_capacity / total_capacity * 100) if total_capacity > 0 else 0
    return pd.Series({
        'Total_H2_Capacity': total_capacity,
        'High_WS_Capacity': high_ws_capacity,
        'Pct_High_WS': pct_high_ws
    })

def map_status(status):
    if status == 'operating':
        return 'operating'
    elif status in ['announced', 'construction', 'pre-construction']:
        return 'pre_construction_announced'
    else:
        return 'other'

hydrogen_df['Status_Group'] = hydrogen_df['Status'].apply(map_status)

result = hydrogen_df.groupby(['Country/area', 'Status_Group']).apply(compute_capacity_metrics).reset_index()

final_result = result.pivot(index='Country/area', columns='Status_Group')

final_result.columns = ['_'.join(col).strip() for col in final_result.columns.values]

final_result = final_result.reset_index()

print(final_result)

final_result.to_csv('hydrogen_capacity_by_country.csv', index=False)
