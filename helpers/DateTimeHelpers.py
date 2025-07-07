from datetime import datetime


class DateTimeHelpers:
    @staticmethod
    def BuildLocalDataTime(time: datetime) -> str:
        hour = time.hour
        minute = time.minute
        second = time.second
        ampm = "am" if hour < 12 else "pm"

        hour = hour % 12 or 12

        return f"{hour}:{minute:02}:{second:02}:{ampm}"

    @staticmethod
    def GetReadableTimeBetween(a: datetime, b: datetime = None, separator: str = ' ', dayMoniker: str = 'd', hourMoniker: str = 'h', minuteMoniker: str = 'm', secondMoniker: str = 's', pluralize: str = '') -> str:
        if b is None:
            b = datetime.now()

        t1 = a.replace(tzinfo=None)
        t2 = b.replace(tzinfo=None)

        start = min(t1,t2)
        end = max(t1,t2)
        delta = end - start
        totalSeconds = int(delta.total_seconds())

        days = totalSeconds // 86400
        hours = (totalSeconds % 86400) // 3600
        minutes = (totalSeconds % 3600) // 60
        seconds = totalSeconds % 60
        dayAppend = ''
        hourAppend = ''
        minuteAppend = ''
        secondAppend = ''
        if (not days == 1):
            dayAppend = pluralize
        if (not hours == 1):
            hourAppend = pluralize
        if (not minutes == 1):
            minuteAppend = pluralize
        if (not seconds == 1):
            secondAppend = pluralize
        

        parts = []
        if (days > 0):
            parts.append(f"{days}{dayMoniker}{dayAppend}")
        if hours > 0 or days > 0:
            parts.append(f"{hours}{hourMoniker}{hourAppend}")
        if minutes > 0 or hours > 0 or days > 0:
            parts.append(f"{minutes}{minuteMoniker}{minuteAppend}")
        parts.append(f"{seconds}{secondMoniker}{secondAppend}")

        return separator.join(parts)

    @staticmethod
    def GetLongReadableTimeBetween(a: datetime, b: datetime = None) -> str:
        return DateTimeHelpers.GetReadableTimeBetween(a,b,
                                                      separator=', ',
                                                      dayMoniker=' day',
                                                      hourMoniker=' hour',
                                                      minuteMoniker=' minute',
                                                      secondMoniker=' second',
                                                      pluralize='s')

    @staticmethod
    def HourSafeToString(date: datetime, f:str) -> str:
        f = f.replace("%-I", str(date.strftime("%I").lstrip('0')))
        f = f.replace("%-H", str(date.strftime("%H").lstrip('0')))

        return date.strftime(f)

    @staticmethod
    def Equal(d1:datetime, d2: datetime) -> bool:
        t1 = d1.replace(tzinfo=None)
        t2 = d2.replace(tzinfo=None)
        return t1 == t2

    @staticmethod
    def LessThan(d1:datetime, d2: datetime) -> bool:
        t1 = d1.replace(tzinfo=None)
        t2 = d2.replace(tzinfo=None)
        return t1 < t2

    @staticmethod
    def GreaterThan(d1:datetime, d2: datetime) -> bool:
        t1 = d1.replace(tzinfo=None)
        t2 = d2.replace(tzinfo=None)
        return t1 > t2

    @staticmethod
    def LessThanOrEqual(d1:datetime, d2: datetime) -> bool:
        t1 = d1.replace(tzinfo=None)
        t2 = d2.replace(tzinfo=None)
        return t1 <= t2

    @staticmethod
    def GreaterThanOrEqual(d1:datetime, d2: datetime) -> bool:
        t1 = d1.replace(tzinfo=None)
        t2 = d2.replace(tzinfo=None)
        return t1 >= t2

    @staticmethod
    def BetweenOrEqual(d1:datetime, d2: datetime, d3: datetime) -> bool:
        t1 = d1.replace(tzinfo=None)
        t2 = d2.replace(tzinfo=None)
        t3 = d3.replace(tzinfo=None)
        return t1 <= t2 <= t3

    @staticmethod
    def BetweenNotEqual(d1:datetime, d2: datetime, d3: datetime) -> bool:
        t1 = d1.replace(tzinfo=None)
        t2 = d2.replace(tzinfo=None)
        t3 = d3.replace(tzinfo=None)
        return t1 < t2 < t3