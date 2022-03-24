from datetime import datetime, date, time, timedelta

today = date.today()
print(today)
last = datetime.now()
last = last.date()
print(time)
if last == today:
    print("same")
else:
    print("different")
