class Delay:
    OneSecond:int = 1000
    OneMinute:int = 60 * 1000
    OneHour:int = 60 * 60 * 1000
    OneDay:int = 24 * 60 * 60 * 1000

    def FromSeconds(seconds:int) -> int:
        return 1000 * seconds

    def FromMinutes(minutes:int) -> int:
        return 1000 * 60 * minutes

    def FromHours(hours:int) -> int:
        return 1000 * 60 * 60 * hours

    def FromDays(days:int) -> int:
        return 1000 * 60 * 60 * 24 * days
