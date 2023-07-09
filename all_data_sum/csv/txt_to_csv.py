import os
import csv

CATEG = "Construction"
PATH = r'/home/xaiplanet/xai_workspace/nlp_integrate/all_data_sum'
SUM_PATH = PATH + r'/{}'.format(CATEG)
CSV_PATH = PATH + r'/csv'

with os.scandir(SUM_PATH) as entries:
    files = [entry for entry in entries if entry.is_file() and '.txt' in entry.name]

to_csv = []
for f in files:
    with open(f, 'r', encoding="utf-8") as r:
        row = [f'{CATEG}', r.read().replace('\n', '\\n')]
        r.close()
    to_csv.append(row)

with open(CSV_PATH + r'/{}.csv'.format(CATEG), 'w', encoding="utf-8-sig", newline='') as w:
    wr = csv.writer(w)
    for c in to_csv:
        wr.writerow(c)
    w.close()