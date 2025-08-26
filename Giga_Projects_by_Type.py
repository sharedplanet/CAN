#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 17:05:39 2025

@author: manickamvalliappan
"""

import pandas as pd

df = pd.read_csv('master_power.csv')

df = df.rename(columns={
    'Type': 'Type',
    'Country/area': 'Country',
    'Capacity (MW)': 'Capacity',
    'Status': 'Status'
})
df['Type'] = df['Type'].str.lower().str.strip()
df['Country'] = df['Country'].str.strip()
df['Status'] = df['Status'].str.lower().str.strip()

focus_countries = [
    "Australia", "Canada", "Chile", "China", "Colombia", "Egypt",
    "Germany", "India", "Japan", "Kenya", "Namibia", "Pakistan",
    "Philippines", "Serbia", "United Arab Emirates", "Uruguay", "Vietnam"
]
df = df[df['Country'].isin(focus_countries)]

prospective_statuses = {'pre-construction', 'announced', 'construction'}
df['Category'] = df['Status'].apply(lambda x: 'Prospective' if x in prospective_statuses else ('Operating' if x == 'operating' else None))
df = df[df['Category'].isin(['Operating', 'Prospective'])]

types = ['solar', 'wind', 'hydropower', 'geothermal', 'biomass']

all_results = []

for category in ['Operating', 'Prospective']:
    subset = df[df['Category'] == category]
    subset_over_1000 = subset[subset['Capacity'] >= 1000]

    total_capacity = subset.groupby('Country')['Capacity'].sum()
    total_plants = subset.groupby('Country').size()
    over_1000_capacity = subset_over_1000.groupby('Country')['Capacity'].sum()
    over_1000_plants = subset_over_1000.groupby('Country').size()

    result = pd.DataFrame(index=focus_countries)
    result[f'Proportion of MW >1000 MW ({category.lower()})'] = over_1000_capacity / total_capacity
    result[f'Proportion of plants >1000 MW ({category.lower()})'] = over_1000_plants / total_plants

    for energy_type in types:
        type_df = subset[subset['Type'] == energy_type]
        type_over_1000 = type_df[type_df['Capacity'] >= 1000]
        total_type_capacity = type_df.groupby('Country')['Capacity'].sum()
        over_1000_type_capacity = type_over_1000.groupby('Country')['Capacity'].sum()
        col_name = f'Proportion of MW >1000 MW for {energy_type} ({category.lower()})'
        result[col_name] = over_1000_type_capacity / total_type_capacity

    all_results.append(result)

final_result = pd.concat(all_results, axis=1)
final_result = final_result.fillna(0)
final_result.to_csv('gigaproject_proportions_by_status.csv')
print(final_result)

breakdown_results = []

for category in ['Operating', 'Prospective']:
    subset = df[df['Category'] == category]
    subset_over_1000 = subset[subset['Capacity'] >= 1000]

    total_giga_capacity = subset_over_1000.groupby('Country')['Capacity'].sum()
    giga_by_type = subset_over_1000.groupby(['Country', 'Type'])['Capacity'].sum().unstack(fill_value=0)
    giga_breakdown = giga_by_type.div(total_giga_capacity, axis=0)
    giga_breakdown = giga_breakdown.add_suffix(f' ({category.lower()})')
    breakdown_results.append(giga_breakdown)

final_breakdown = pd.concat(breakdown_results, axis=1).fillna(0)
final_breakdown.to_csv("gigaproject_breakdown_by_type.csv")
print(final_breakdown)
