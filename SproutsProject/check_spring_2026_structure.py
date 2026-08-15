#!/usr/bin/env python3
import csv

print("CHEF CSV STRUCTURE:")
with open('chef_avail_spring_2026.csv', encoding='utf-8') as f:
    rows = list(csv.reader(f))
    print(f"Total columns: {len(rows[0])}")
    print("\nFirst row (first 25 columns):")
    for i, val in enumerate(rows[0][:25]):
        print(f"  Col {i}: {val}")

print("\n\nINTERN CSV STRUCTURE:")
with open('intern_avail_spring_2026.csv', encoding='utf-8') as f:
    rows = list(csv.reader(f))
    print(f"Total columns: {len(rows[0])}")
    print("\nFirst row (columns 30-50 for availability):")
    for i in range(30, min(50, len(rows[0]))):
        print(f"  Col {i}: {rows[0][i]}")
