#!/usr/bin/env python3
"""Test market prices tool integration"""

import sys
sys.path.insert(0, 'src')

from agents.supervisor_simple import supervisor_simple_with_prices

# Test query about market prices
query = "[User Location: Nashik, Maharashtra]\n\nWhat are the current market prices for tomatoes in Nashik?"

print("Testing market price query with wrapper...")
print(f"Query: {query}\n")

response = supervisor_simple_with_prices(query)
print(f"Response:\n{response}")
