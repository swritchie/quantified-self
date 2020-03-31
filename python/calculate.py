#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 14:58:28 2019

@author: skylarritchie
"""

# =============================================================================
# Import modules
# =============================================================================

import config as c
import define_functions as df
import os
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
summary_df = pd.read_sql(
        'SELECT * FROM summary', 
        engine
        ).set_index('start_datetime')
    
# =============================================================================
# Calculate effectiveness points for...
# =============================================================================

# 1 - Spending time with God
calc_df = pd.DataFrame(
        df.calc_effectivness_points(
                '1 - Spending time with God', 
                summary_df['1 - Spending time with God']
                ),
        columns=['1 - Spending time with God'],
        index=summary_df.index
        )

# 2 - Spending time with Laura
calc_df['2 - Spending time with Laura'] = df.calc_effectivness_points(
        '2 - Spending time with Laura', 
        summary_df['2 - Spending time with Laura']
        )

# 3 - Spending time with family
calc_df['3 - Spending time with family'] = df.calc_effectivness_points(
        '3 - Spending time with family', 
        summary_df['3 - Spending time with family']
        )

# 4 - Spending time with friends
calc_df['4 - Spending time with friends'] = df.calc_effectivness_points(
        '4 - Spending time with friends', 
        summary_df['4 - Spending time with friends']
        )

# 5 - Sleeping
calc_df['5 - Sleeping'] = df.calc_effectivness_points(
        '5 - Sleeping', 
        summary_df['5 - Sleeping']
        )

# 6 - Reflecting
calc_df['6 - Reflecting'] = df.calc_effectivness_points(
        '6 - Reflecting', 
        summary_df['6 - Reflecting']
        )

# 7 - Serving
calc_df['7 - Serving'] = df.calc_effectivness_points(
        '7 - Serving', 
        summary_df['7 - Serving']
        )

# 8 - Working
calc_df['8 - Working'] = df.calc_effectivness_points(
        '8 - Working', 
        summary_df['8 - Working']
        )

# 9 - Exercising
calc_df['9 - Exercising'] = df.calc_effectivness_points(
        '9 - Exercising', 
        summary_df['9 - Exercising']
        )

# 10 - Waste
calc_df['10 - Waste'] = df.calc_effectivness_points(
        '10 - Waste', 
        summary_df['10 - Waste']
        )

# =============================================================================
# Write to database
# =============================================================================

calc_df.to_sql(
        'calculations',
        engine,
        if_exists='replace'
        )
