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
# Write to database
# =============================================================================

engine = sqlalchemy.create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(
        c.config['username'],
        c.config['password'],
        c.config['host'],
        c.config['port'],
        c.config['database']
        ))
df.loc[:, ['note', 'datetime', 'happiness']].to_sql(
        'daylio',
        engine,
        if_exists='fail',
        index=False
        )