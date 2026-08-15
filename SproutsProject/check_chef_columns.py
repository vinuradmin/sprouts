import csv
rows = list(csv.reader(open('chef_avail_spring_2026.csv', encoding='utf-8')))
print('Chef row columns 15-25:')
for i in range(15, min(25, len(rows[0]))):
    print(f'  Col {i}: {rows[0][i]}')
