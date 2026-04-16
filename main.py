import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from data import fetch_data

athlete_id = ""
event = ""

races = fetch_data(athlete_id, event)

years = []
for race in races:
    if race.date.year not in years:
        years.append(race.date.year)

fig, axes = plt.subplots(1, len(years), sharey=True, figsize=(10, 5))
fig.subplots_adjust(wspace=0.001)
axes : list[plt.Axes]

for i, ax, in enumerate(axes):
    ax.set_title(years[i])
    if i == 0:
        ax.spines["right"].set_visible(True)
    elif i == len(axes) - 1:
        ax.spines["left"].set_visible(True)
        axes[-1].tick_params(left=False)
    else:
        ax.spines["right"].set_visible(True)
        ax.spines["left"].set_visible(True)
        axes[i].tick_params(left=False)

for race in races:
    ax = axes[years.index(race.date.year)]
    match race.best:
        case 0:
            color = "black"
        case 1:
            color = "blue"
        case 2:
            color = "red"
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    
    ax.scatter(race.date, race.time.seconds, color=color)
    ax.yaxis.set_major_formatter(lambda x, pos: f"{int(x // 60)}:{x % 60:05.2f}")
    
plt.show()