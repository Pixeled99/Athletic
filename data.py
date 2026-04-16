from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import re
import json
import os

class Time:
    def __init__(self, seconds : float = None):
        self.seconds = seconds
        
    def __str__(self):
        return str(self.seconds)
        
    def present(self):
        minutes = int(self.seconds // 60)
        seconds = self.seconds % 60
        return f"{minutes}:{seconds:05.2f}"

class Race:
    def __init__(self, place : int = None, time : Time = None, date : datetime = None, best : int = None):
        if isinstance(date, str):
            self.date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        else:
            self.date = date
        if isinstance(time, str):
            self.time = Time(float(time))
        else:
            self.time = time
        self.place = place
        self.best = best
        
    def __repr__(self):
        match self.best:
            case 0:
                best = ""
            case 1:
                best = "SB"
            case 2:
                best = "PB" 
        return f"{self.date.date()} - {self.time} - {self.place} {best}"
    
regex_query = r"^(\S*\s\S*\s\S*)"

def fetch_data(user_id : str, event : str, update : bool = False) -> list[Race]:
    races = []
     
    if os.path.exists(f"{user_id}_{event.replace(' ', '_')}.json") and not update:
        with open(f"{user_id}_{event.replace(' ', '_')}.json", "r") as f:
            for json_string in json.load(f):
                race_data = json.loads(json_string)
                races.append(Race(**race_data))
        return races
    
    driver = webdriver.Chrome()
    
    url = f"https://www.athletic.net/athlete/{user_id}/track-and-field/all"
    driver.get(url)
    
    elem = driver.find_element(By.TAG_NAME, "shared-athlete-bio-results")
    seasons = elem.find_elements(By.XPATH, f"//*[@id='anetMain']/anet-site-app/ng-component/div/div/div[2]/shared-athlete-bio-results/div")
    current_event = ""
    
    for season in seasons:
        for table in season.find_elements(By.TAG_NAME, "shared-athlete-bio-result-table-tf"):
            for row in table.find_elements(By.TAG_NAME, "tr"):
                if row.get_attribute("result-id") is None:
                    current_event = row.text
                elif current_event == event:
                    info = row.text.split("\n")
                    best = 0
                    
                    if info[0][:-1].isdigit():
                        place = int(info[0])
                    else:
                        continue
        
                    time = info[1].split(":")
                    time = Time(round(float(int(time[0]) * 60) + float(time[1]), 2))
                    
                    search = re.match(regex_query, info[2])
                    if search is not None:
                        date = datetime.strptime(search.group(1), "%b %d, %Y")
                    else:
                        date = datetime.strptime(re.match(regex_query, info[3]).group(1), "%b %d, %Y")
                        best = 1 if "SB" in info[2] else 2
                        
                    races.append(Race(place, time, date, best))

    races.sort(key=lambda x: x.date)
    
    driver.close()
    
    races_json = [json.dumps(race.__dict__, default=str) for race in races]
    
    with open(f"{user_id}_{event.replace(' ', '_')}.json", "w") as f:
        json.dump(races_json, f)
    
    return races