# Converti SPEIT class schedule to ICS format

This project converts a SPEIT class schedule to ICS file that can be imported to popular calendar apps.

## Arguments

You will need to modify these variables to make it work

```python
SHEET_NAMES = ['W1-8', 'W9-16'] # Sheet names in the xlsx file
FILENAME = 'file.xlsx' # Filename
CONFIG_TIMETABLE_COL_IDX = 1 # Column index of the timetable
CONFIG_DATE_ROW_IDX = 1 # Row index of the date
CONFIG_WEEDDAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] # Week days to filter
TZ = timezone('Asia/Shanghai') # Default timezone for time that are not specified
```
