import csv

rows = list(csv.reader(open('chef_avail_spring_2026.csv', encoding='utf-8')))
print(f'Total columns: {len(rows[0])}')
print('\nAll columns:')
for i, val in enumerate(rows[0]):
    display_val = val[:50] if len(val) > 50 else val
    print(f'Col {i}: {display_val}')
