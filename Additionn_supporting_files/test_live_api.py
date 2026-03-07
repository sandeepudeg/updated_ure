#!/usr/bin/env python3
"""Test live API data fetching"""

import sys
sys.path.insert(0, 'src')

from agents.supervisor_simple import get_market_prices

# Test with just commodity and state (no district filter)
print("Test 1: Tomato in Maharashtra (no district)")
result = get_market_prices('Tomato', '', 'Maharashtra')
print(result)
print("\n" + "="*60 + "\n")

# Test with just commodity (no state or district)
print("Test 2: Tomato (no filters)")
result = get_market_prices('Tomato', '', '')
print(result)
