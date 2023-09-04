import datetime 
import collections
# test birthdays list
users = [
    {
        "name": "Anna-Sofiya",
        "birthday": datetime.date(1985, 8, 31)
    },
    {
        "name": "Viktoriya",
        "birthday": datetime.date(1985, 9, 1)
    },
    {
        "name": "Solomiya",
        "birthday": datetime.date(1990, 9, 3)
    },
    {
        "name": "Oleksandr",
        "birthday": datetime.date(1998, 9, 6)
    },
    {
        "name": "Mark",
        "birthday": datetime.date(2005, 9, 5)
    },
    {
        "name": "Bogdan",
        "birthday": datetime.date(1967, 10, 1)
    }
]


def get_birthdays_per_week(users: list):
    today = datetime.date.today()
    birthdayWeekStart = today + datetime.timedelta(days=7-today.weekday())
    birthdayWeekEnd = birthdayWeekStart + datetime.timedelta(days=4)
    daysToIncludeInMonday = datetime.timedelta(days=2)
    # collection for results
    birthdaysForWeek = collections.defaultdict(list)
    for user in users:
        # ammend year if next week is split between years
        if datetime.date(
                today.year,
                user["birthday"].month,
                user["birthday"].day
        ) >= birthdayWeekStart - daysToIncludeInMonday:
            birthdayYear = today.year
        else:
            birthdayYear = today.year+1

        birthdayDateThisYear = datetime.date(
            birthdayYear,
            user["birthday"].month,
            user["birthday"].day
        )
        # group weekend and Mon, otherwise take day of the week for Tue-Fri
        if birthdayDateThisYear >= birthdayWeekStart - daysToIncludeInMonday \
                and birthdayDateThisYear <= birthdayWeekStart:
            birthdaysForWeek[birthdayWeekStart.strftime(
                "%A")].append(user["name"])
        elif birthdayDateThisYear <= birthdayWeekEnd:
            birthdaysForWeek[birthdayDateThisYear.strftime(
                "%A")].append(user["name"])
    # output results
    for day, persons in birthdaysForWeek.items():
        print(f"{day}: {', '.join(persons)}")
    return


get_birthdays_per_week(users)