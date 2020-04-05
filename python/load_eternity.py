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
import os
import pandas as pd
import sqlalchemy

# =============================================================================
# Read in data
# =============================================================================

dir_sg = input('What is your directory?\n')
file_sg = input('What is your file?\n')
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

engine = sqlalchemy.create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(
        c.config['username'],
        c.config['password'],
        c.config['host'],
        c.config['port'],
        c.config['database']
        ))
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