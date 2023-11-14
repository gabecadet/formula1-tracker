from bs4 import BeautifulSoup
import requests
import csv
from enum import Enum

class Choice(Enum):
    """
    enumeration representing menu choices
    """
    ADD_RACE = 1
    ADD_DRIVER = 2
    RECORD_RESULT = 3
    DISPLAY_POSITION = 4
    DISPLAY_STANDINGS = 5
    LOOKUP_CHAMPION = 6
    LOOKUP_CONSTRUCTORS = 7
    SCRAPE_F1_CRASH_DATA = 8
    EXIT = 9

class Driver:
    """
    class for f1 driver
    """
    def __init__(self, name, team):
        """
        intialize a driver instance

        arguments: 
            name is a string that has the name of the driver
            team is the Team that the driver is on

        """
        self.name = name
        self.team = team
        self.points = 0
        self.position = None

    def __str__(self):
        """
        returns string that represents the driver
        """
        return f"Driver: {self.name}, Team: {self.team.name}, Points: {self.points}, Position: {self.position}"

class Team:
    """
    class that represents an f1 team
    """
    def __init__(self, name):
        """
        initializes a Team instance
        
        arguments:
            name is a string that has the name of the team
        """
        self.name = name
        self.points = 0
        self.drivers = []

    def __str__(self):
        """
        Return a string representation of the team.
        """
        return f"Team: {self.name}, Points: {self.points}, Drivers: {[driver.name for driver in self.drivers]}"

class RaceResult:
    """
    class that represents the result of an f1 race
    """
    def __init__(self, driver, position):
        """
        initialiazes a RaceResult instance

        arguments:
            driver that holds the Driver who achived the position
            position is an int that is the position of the driver in the race
        """
        self.driver = driver
        self.position = position

class Race:
    """
    class that represents an f1 race
    """
    def __init__(self, name):
        """
        initializes a race instance

        argument:
            name is a string that has the name of the race
        """
        self.name = name
        self.results = []

    def __str__(self):
        """
        returns a string representation of the race
        """
        return f"Race: {self.name}"

POINT_SCALE = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}

drivers_dict = {}
teams_dict = {}
race_dict = {}
champions_dict = {}
constructors_dict = {}

def load_champions():
    """
    load the champions info from the file
    """
    with open('f1info.csv', 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            year, champion = row
            champions_dict[int(year)] = champion.strip()

def load_constructors():
    """
    load the constructors information from the file
    """
    with open('f1info2.csv', 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            year, constructor = row
            constructors_dict[int(year)] = constructor.strip()

def lookup_champion():
    """
    look up the drivers info from a year
    """
    year = int(input("Enter year: "))
    champion = champions_dict.get(year)
    if champion:
        print(f"The drivers champion of {year} was {champion}.")
    else:
        print(f"No information available for the year {year}.")

def lookup_constructors():
    """
    look up the constructors champion from a year
    """
    year = int(input("Enter year: "))
    constructor = constructors_dict.get(year)
    if constructor:
        print(f"The constructors champion of {year} was {constructor}.")
    else:
        print(f"No information available for the year {year}.")

def add_driver():
    """
    add new driver
    """
    print("Enter driver's name and their team, separated by a comma. When finished, type 'DONE':")
    while True:
        data = input("> ")
        if data.lower() == 'done':
            break
        try:
            name, team_name = [d.strip() for d in data.split(',')]
            if not name or not team_name:
                print("Invalid input, please try again.")
                continue
            team = teams_dict.get(team_name)
            if not team:
                team = Team(team_name)
                teams_dict[team_name] = team
            driver = Driver(name, team)
            drivers_dict[name] = driver
            team.drivers.append(driver)
        except ValueError:
            print("Invalid input, please provide data in format 'driver_name, team_name'.")

def add_race():
    """
    add new race 
    """
    print("Enter race names, one per line. When finished, type 'DONE':")
    while True:
        name = input("> ")
        if name.lower() == 'done':
            break
        name = name.strip()
        if name:
            race = Race(name)
            race_dict[name] = race

def record_race_result():
    """
    record race result
    """
    race_name = input("Enter race name: ").strip()

    while True:
        data = input("Enter driver's name and position, separated by a comma. When finished, type 'DONE'").split(',')
        if len(data) < 2 or data[0].lower() == 'done':
            break

        driver_name, position = [d.strip() for d in data]

        if int(position) < 1:
            print("Invalid position.")
            continue

        race = race_dict.get(race_name)
        driver = drivers_dict.get(driver_name)

        if race and driver:
            result = RaceResult(driver, int(position))
            race.results.append(result)
            points = POINT_SCALE.get(result.position, 0)
            result.driver.points += points
            result.driver.team.points += points
        else:
            print("Invalid driver name or race name.")



def finish_race():
    """
    finish a race and calculate the driver and teams points
    """
    race_names = input("Enter race name (or multiple names separated by commas): ").split(',')
    for race_name in race_names:
        race_name = race_name.strip()
        race = race_dict.get(race_name)

        if race:
            for result in race.results:
                points = POINT_SCALE.get(result.position, 0)
                result.driver.points += points
                result.driver.team.points += points

def display_driver_position():
    """
    display positions of all drivers
    """
    sorted_drivers = sorted(drivers_dict.values(), key=lambda driver: driver.points, reverse=True)

    for i, driver in enumerate(sorted_drivers, 1):
        driver.position = i

    for driver in sorted_drivers:
        print(driver)


def display_team_standings():
    """
    display team standings with positions
    """
    sorted_teams = sorted(teams_dict.values(), key=lambda team: team.points, reverse=True)

    for i, team in enumerate(sorted_teams, 1):
        print(f"Position: {i}, {team}")


def scrape_f1_crash_data():
    """
    scrape crash info from website
    """
    url = "https://f1-dnf-stats.fly.dev/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            for row in rows[1:]:
                columns = row.find_all('td')
                if columns:
                    driver = columns[0].text.strip()
                    dnf_count = columns[1].text.strip()
                    percent = columns[2].text.strip()
                    print(f"Season: {driver}, DNF Count: {dnf_count}, DNF Percentage: {percent}")
        else:
            print("No crash data table found on the page.")
    else:
        print("Failed to scrape the F1 crash data website.")

def main():
    """
    main function to run program
    """
    load_champions()
    load_constructors()
    while True:
        print("1. Add Current Season Race\n2. Add Current Season Driver\n3. Record Current Season Race Result\n4. Display Current Driver Position\n5. Display Current Team Standings\n6. Lookup Drivers Previous Champion\n7. Lookup Previous Constructors Champion\n8. Display F1 Crash Statistics\n9. Exit")
        try:
            choice = Choice(int(input("Enter your choice: ")))
            if choice == Choice.ADD_RACE:
                add_race()
            elif choice == Choice.ADD_DRIVER:
                add_driver()
            elif choice == Choice.RECORD_RESULT:
                record_race_result()
            elif choice == Choice.DISPLAY_POSITION:
                display_driver_position()
            elif choice == Choice.DISPLAY_STANDINGS:
                display_team_standings()
            elif choice == Choice.LOOKUP_CHAMPION:
                lookup_champion()
            elif choice == Choice.LOOKUP_CONSTRUCTORS:
                lookup_constructors()
            elif choice == Choice.SCRAPE_F1_CRASH_DATA:
                scrape_f1_crash_data()
            elif choice == Choice.EXIT:
                break
            else:
                print("Invalid choice, please try again.")
        except ValueError:
            print("Invalid input, please try again.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()


