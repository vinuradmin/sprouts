import csv

rows = list(csv.reader(open('C:/Users/pierr/OneDrive/Documents/chef_avail_spring_2026.csv', encoding='utf-8')))
print('Checking chef availability data for issues...\n')

for i, row in enumerate(rows[1:10]):
    print(f'Row {i+1}: {row[0]} - {row[1]}')
    for day_idx, day in enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']):
        avail = row[8 + day_idx] if len(row) > 8 + day_idx else ''
        if avail and avail.strip():
            # Check for problematic patterns
            if ', ' in avail and avail.endswith(', '):
                print(f'  {day}: TRAILING COMMA AND SPACE: [{avail}]')
            elif avail.endswith(','):
                print(f'  {day}: TRAILING COMMA: [{avail}]')
            elif '  ' in avail:
                print(f'  {day}: DOUBLE SPACE: [{avail}]')
