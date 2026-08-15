import csv

rows = list(csv.DictReader(open('spring_2026_intern_restaurant_options_with_overlaps.csv', encoding='utf-8')))
print('Sample rows with overlap information:\n')
print(f"{'Intern Name':<20} | {'Restaurant':<25} | {'Commute':<8} | {'Days with Overlap'}")
print("-" * 100)
for row in rows[:10]:
    print(f"{row['Intern Name']:<20} | {row['Restaurant']:<25} | {row['Commute (min)']:>3} min | {row['Days with Overlap']}")
