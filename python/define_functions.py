#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 15:24:28 2019

@author: skylarritchie
"""

# =============================================================================
# Import modules
# =============================================================================

import numpy as np
import pandas as pd
import parameters as p

# =============================================================================
# calc_activity_values()
# =============================================================================
  
def calc_activity_values(act_name, max_act=0, min_act=100):
    '''
    Calculates range of activity values by hundredths between min and max
    for given activity
    
    Parameters:
    - act_name (string): one of ten activities:
       - '1 - Spending time with God'
       - '2 - Spending time with Laura'
       - '3 - Spending time with family'
       - '4 - Spending time with friends'
       - '5 - Sleeping'
       - '6 - Reflecting'
       - '7 - Serving'
       - '8 - Working'
       - '9 - Exercising'
       - '10 - Waste'
    - max_act (int): maximum activity value
    - min_act (int): minimum activity value
    
    Returns:
    series: floats between min and max for given activity
    '''
    # Assign to variables
    max_act = max(max_act, p.parameters[act_name]['max_act'])
    min_act = min(min_act, p.parameters[act_name]['min_act'])
    
    # Return result
    return pd.Series([x / 100.0 for x in range(
            int(min_act * 100), 
            int(max_act * 100) + 1
            )])

# =============================================================================
# calc_effectiveness_points()
# =============================================================================
    
def calc_effectivness_points(act_name, act_values):
    '''
    Calculates effectiveness points corresponding to given activity level
    (or range thereof)
    
    Parameters:
    - act_name (string): one of ten activities:
       - '1 - Spending time with God'
       - '2 - Spending time with Laura'
       - '3 - Spending time with family'
       - '4 - Spending time with friends'
       - '5 - Sleeping'
       - '6 - Reflecting'
       - '7 - Serving'
       - '8 - Working'
       - '9 - Exercising'
       - '10 - Waste'
    - act_values (series): activity level or range of them
    
    Returns:
    series: floats representing effectivness points  
    '''    
    return (
            (p.parameters[act_name]['max_eff'] * 2) / 
            (1 + np.exp(
                    -p.parameters[act_name]['steepness'] * 
                    (act_values - 
                     p.parameters[act_name]['act_midpoint']))
            ) -
            p.parameters[act_name]['max_eff']
            )