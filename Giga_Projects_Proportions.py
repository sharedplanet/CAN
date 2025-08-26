#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 16:53:07 2025

@author: manickamvalliappan
"""

import pandas as pd

df = pd.read_csv('master_power.csv')

df = df.rename(columns={
    'Type': 'Type',
    'Country/area': 'Country',
    'Capacity (MW)': 'Capacity'
})

df_over_1000 = df[df['Capacity'] > 1000]

total_capacity_by_country = df.groupby('Country')['Capacity'].sum()
total_plants_by_country = df.groupby('Country').size()
over_1000_capacity_by_country = df_over_1000.groupby('Country')['Capacity'].sum()
over_1000_plants_by_country = df_over_1000.groupby('Country').size()

result = pd.DataFrame(index=total_capacity_by_country.index)

result['Proportion of MW >1000 MW'] = over_1000_capacity_by_country / total_capacity_by_country
result['Proportion of plants >1000 MW'] = over_1000_plants_by_country / total_plants_by_country

types = ['solar', 'wind', 'hydro', 'geothermal', 'biomass']

for energy_type in types:
    type_df = df[df['Type'].str.lower() == energy_type]
    type_over_1000 = type_df[type_df['Capacity'] > 1000]
    total_type_capacity = type_df.groupby('Country')['Capacity'].sum()
    over_1000_type_capacity = type_over_1000.groupby('Country')['Capacity'].sum()
    col_name = f'Proportion of MW >1000 MW for {energy_type}'
    result[col_name] = over_1000_type_capacity / total_type_capacity

result = result.fillna(0)
result.to_csv('proportions_by_country.csv')
print(result)
