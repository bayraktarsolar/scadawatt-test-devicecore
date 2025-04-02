import datetime
import openpyxl

# Define variable to load the dataframe
dataframe = openpyxl.load_workbook("macs.xlsx", read_only=True)

# Define variable to read sheet
ws = dataframe.active

ara = "7b3a"
ara = ara[0:2] + ":" + ara[2:4]

start = datetime.datetime.now()
# Iterate the loop to read the cell values
for row in ws.rows:
    if row[0].value == "5c:ad:a3:a7:" + ara:
        print(row[11].value)
        break

finish = datetime.datetime.now()
print((finish-start))