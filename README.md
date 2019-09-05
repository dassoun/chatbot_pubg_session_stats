## Intro

**Chatbot PUBG Session Stats** is a script written in Python 2.7

The goal of this script is to get datas from the PUBG APIs, and update files with these datas, so they can be diplayed in Streamlabs OBS, for a given session of gaming (from a start date to the current time).
This is a **Streamlabs Chatbot** compliant version of **PUBG Session Stats**

Please note that I discovered Python while writing this script, so feel free to comment the code, and give me some advices.

  
## Configuration

the script has to be configured through the UI:
-  **PUBG API Key**: PUBG API Developer Key, wich can be found here: https://developer.pubg.com/.
-  **Player's Name**: the name of the player you want to track.
-  **Data Files Directory**: the path for the data files generated by the script. **The path has to already exist**.
-  **Timezone**: the timezone you are in (we can get the timezones here: https://www.php.net/manual/fr/timezones.php).
-  **Frequency (minutes)**: the time, in minutes between two datas refreshs


## Dependencies

You may have to install some libs to run the script successfully.
I found the libs to install, and the way to do it by searching the errors messages in my favourite serch engine, so don't hesitate to do the same.

  
## Let's make it work !

A zip file containing this project has to be imported in **Streamlabs Chatbot** scripts.

The text files have to be linked to text fields in Streamlabs OBS.

The available datas are:

- **Number of games played** (pubg_games.txt)
- **Number of kills** (pubg_kills.txt)
- **Number of wins** (pubg_wins.txt)
- **Number of assists** (pubg_assists.txt)
- **Number of DBNOs** (pubg_dbnos.txt)
- **Kills / Deaths ratio** (pubg_kd.txt)
- **(Kills + Assists) / Deaths ratio** (pubg_kda.txt)
- **Best rank** (pubg_top.txt)
- **Average rank** (pubg_avg_rank.txt)
- **Total damages** (pubg_damage_total.txt)
- **Max damages in a game** (pubg_damage_max.txt)
- **Average damages** (pubg_damage_avg.txt)
