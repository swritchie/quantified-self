#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 13:40:37 2019

@author: skylarritchie
"""

# =============================================================================
# Import modules
# =============================================================================

import config as c
import numpy as np
import pandas as pd
import sqlalchemy

# =============================================================================
# Read in data
# =============================================================================

engine = sqlalchemy.create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(
        c.config['username'],
        c.config['password'],
        c.config['host'],
        c.config['port'],
        c.config['database']
        ))
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
        )['duration'].sum().unstack().fillna(0).resample('W-SAT').sum()

# =============================================================================
# Write to database
# =============================================================================

eternity_df2.to_sql(
        'summary',
        engine,
        if_exists='replace'
        )