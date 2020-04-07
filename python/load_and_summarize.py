#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 21:09:25 2019

@author: skylarritchie
"""

# =============================================================================
# Import modules
# =============================================================================

import config as c
import numpy as np
import os
import pandas as pd
import sqlalchemy

# =============================================================================
# Read in Daylio data
# =============================================================================

dir_sg = input('What is your directory?\n')
file_sg = input('What is your Daylio file?\n')
df = pd.read_csv(os.path.join(dir_sg, file_sg))

# =============================================================================
# Calculate datetime
# =============================================================================

df.sort_values(['full_date', 'time'], inplace=True)
df['time'] = int(len(df) / 3) * [
        '00:00:00', '08:00:00', '16:00:00'
        ]
df['datetime'] = pd.to_datetime(df['full_date'] + ' ' + df['time'])

# =============================================================================
# Map mood to numerical scale
# =============================================================================

df['happiness'] = df['mood'].map({
        'Best': 5,
        'Better': 4,
        'Good': 3,
        'Worse': 2,
        'Worst': 1
        })

# =============================================================================
# Get max datetime in database
# =============================================================================

engine = sqlalchemy.create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(
        c.config['username'],
        c.config['password'],
        c.config['host'],
        c.config['port'],
        c.config['database']
        ))
temp_dt = pd.read_sql('SELECT MAX(datetime) FROM daylio', engine).iloc[0, 0]

# =============================================================================
# Write to database
# =============================================================================

df.loc[
       df['datetime'] > temp_dt, 
       ['note', 'datetime', 'happiness']
       ].to_sql(
        'daylio',
        engine,
        if_exists='append',
        index=False
        )

# =============================================================================
# Read in Eternity data
# =============================================================================

file_sg = input('What is your Eternity file?\n')
df = pd.read_csv(os.path.join(dir_sg, file_sg))

# =============================================================================
# Calculate datetime
# =============================================================================

df['start_datetime'] = pd.to_datetime(df['day'] + ' ' + df['start time'])
df['stop_datetime'] = df['start_datetime'] + pd.to_timedelta(df['duration'])

# =============================================================================
# Strip activity name
# =============================================================================

df['activity_name'] = df['activity name'].str.strip()

# =============================================================================
# Get max stop datetime in database
# =============================================================================

temp_dt = pd.read_sql(
        'SELECT MAX(stop_datetime) FROM eternity', 
        engine
        ).iloc[0, 0]

# =============================================================================
# Write to database
# =============================================================================

df.loc[
        df['stop_datetime'] > temp_dt, 
        ['start_datetime', 'stop_datetime', 'activity_name']
        ].to_sql(
        'eternity',
        engine,
        if_exists='append',
        index=False
        )

# =============================================================================
# Read in Eternity data
# =============================================================================

eternity_df = pd.read_sql('SELECT * FROM eternity', engine)

# =============================================================================
# Aggregate Eternity data by week
# =============================================================================

for temp_sg in ['start_datetime', 'stop_datetime']:
    eternity_df[temp_sg] = pd.to_datetime(eternity_df[temp_sg])
eternity_df['duration'] = np.round((
        eternity_df['stop_datetime'] - eternity_df['start_datetime']
                ).dt.seconds / 3600, 
        2
        )
eternity_df2 = eternity_df.groupby(
        ['start_datetime', 'activity_name']
        )['duration'].sum().unstack().fillna( # Stack and unstack to get all permutations
                0                             # Fill missing
                ).resample('W-SAT').sum().stack().reset_index()
eternity_df2.columns = ['start_datetime', 'activity_name', 'activity_value']

# =============================================================================
# Write to database
# =============================================================================

eternity_df2.to_sql(
        'summary',
        engine,
        if_exists='replace',
        index=False
        )