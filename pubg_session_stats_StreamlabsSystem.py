#---------------------------
#   Import Libraries
#---------------------------
import json
import datetime as DT
import pytz
import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "lib")) #point at lib folder for classes / references

import clr
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

#   Import your Settings class
from Settings_Module import MySettings

import conf

#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = "PUBG session stats"
Website = "https://www.twitch.tv/phobyjuan"
Description = "Track stats of a player for a PUBG session"
Creator = "PhobyJuan"
Version = "0.1.0.0"

#---------------------------
#   Define Global Variables
#---------------------------
global SettingsFile
SettingsFile = ""
global ScriptSettings
ScriptSettings = MySettings()

#---------------------------
#   Update file
#---------------------------
def update_source_file(file_path, value):
    file = open(file_path, "w")
    file.write(value)
    file.close

    return

#---------------------------
#   Init data files
#---------------------------
def init_data_files():
    update_source_file(file_games, "0")
    update_source_file(file_kills, "-")
    update_source_file(file_wins, "-")
    update_source_file(file_assists, "-")
    update_source_file(file_dbno, "-")
    update_source_file(file_kd, "-")
    update_source_file(file_kda, "-")
    update_source_file(file_top, "-")
    update_source_file(file_avg_rank, "-")
    update_source_file(file_total_damages, "-")
    update_source_file(file_max_damages, "-")
    update_source_file(file_avg_damages, "-")

    return

#---------------------------
#   Update datas
#---------------------------
def update_data():
    # Variables initialization
    nb_match        = 0             # Number of played matchs
    nb_kill         = 0             # Number of kills
    nb_win          = 0             # Number of Top 1
    nb_assist       = 0             # Number of assists
    nb_dbno         = 0             # Number of DBNOs
    nb_death        = 0             # Number of deaths
    win_place       = 100           # Best rank
    rank_sum        = 0             # sum of the different rankings to clacule the average rank
    total_damage    = 0             # Total damages
    max_damage      = 0             # Max damages in a game
    avg_damage      = 0             # average damages
    top_repeat      = 0             # How many times the player complete his best rank

    # Set the header for PUBG API calls
    headers = {
        "Authorization": "Bearer " + ScriptSettings.PubgApiKey,
        "Accept": "application/vnd.api+json"
    }

    # Get the list of the matchs for the player
    player_stats_url = conf.CONST_URL + "/" + conf.CONST_PLATFORM_STEAM + "/" + "players?filter[playerNames]=" + ScriptSettings.PlayerName

    r = Parent.GetRequest(player_stats_url, headers)
    res = json.loads(r)

    if res["status"] == 200:
        Parent.Log("PUBG Session Stats", "Successfully Connected!!!")
    else:
        Parent.Log("PUBG Session Stats", "Failed to Connect!!!")
        sys.exit(1)

    player_stat = json.loads(res['response'])

    # We extract the match id list from the player object
    match_id_list = player_stat["data"][0]["relationships"]["matches"]["data"]

    for match in match_id_list:
        match_id = match["id"]
        match_url = conf.CONST_URL + "/" + conf.CONST_PLATFORM_STEAM + "/" + "matches/{}".format(match_id)
        
        match_r = Parent.GetRequest(match_url, headers)
        res = json.loads(match_r)
        
        if res["status"] != 200:
            Parent.Log("PUBG Session Stats", "Failed to Connect!!!")

        match_stat = json.loads(res['response'])

        # Get the creation date of the match datas
        created_at = match_stat["data"]["attributes"]["createdAt"]
        
        dt_created_at = DT.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")

        # Get the start date of the session
        with open(file_session_start) as file:
            dt_session_start = DT.datetime.strptime(file.read(), "%Y-%m-%d %H:%M:%S %Z")

        if dt_created_at >= dt_session_start:
            nb_match += 1

            included_list = match_stat["included"]
            # print(json.dumps(included_list, sort_keys=False, indent=4))

            for included in included_list:
                if (included["type"] == "participant" and included["attributes"]["stats"]["name"] == ScriptSettings.PlayerName):
                    # print(json.dumps(included, sort_keys=False, indent=4))
                    nb_kill += included["attributes"]["stats"]["kills"]
                    if included["attributes"]["stats"]["winPlace"] == 1:
                        nb_win += 1
                    else:
                        nb_death += 1
                    nb_assist += included["attributes"]["stats"]["assists"]
                    try:
                        nb_dbno += included["attributes"]["stats"]["DBNOs"]
                    except KeyError:
                        nb_dbno += 0
                    if included["attributes"]["stats"]["winPlace"] < win_place:
                        win_place = included["attributes"]["stats"]["winPlace"]
                        top_repeat = 1
                    elif included["attributes"]["stats"]["winPlace"] == win_place:
                        top_repeat += 1
                    rank_sum += included["attributes"]["stats"]["winPlace"]
                    total_damage += included["attributes"]["stats"]["damageDealt"]
                    if included["attributes"]["stats"]["damageDealt"] > max_damage:
                        max_damage = round(included["attributes"]["stats"]["damageDealt"])

    if nb_match == 0:
        init_data_files()
    else:
        update_source_file(file_games, str(nb_match))
        update_source_file(file_kills, str(nb_kill))
        update_source_file(file_wins, str(nb_win))
        update_source_file(file_assists, str(nb_assist))
        update_source_file(file_dbno, str(nb_dbno))
        if nb_death > 0:
            update_source_file(file_kd, str(round(float(nb_kill) / float(nb_death), 2)))
            update_source_file(file_kda, str(round(float(nb_kill + nb_assist) / float(nb_death), 2)))
        else:
            update_source_file(file_kd, str(nb_kill))
            update_source_file(file_kd, str(nb_kill + nb_assist))
        # If the top rank occured more than once, we show it
        str_win_place = str(win_place)
        if win_place > 1 and top_repeat > 1:
            str_win_place += " (x{})".format(top_repeat)
        update_source_file(file_top, str_win_place)
        update_source_file(file_avg_rank, str(round(float(rank_sum) / float(nb_match), 2)))
        update_source_file(file_total_damages, str(round(total_damage)))
        if nb_match > 0:
            avg_damage = str(round(float(total_damage) / float(nb_match), 2))
        else:
            avg_damage = 0
        update_source_file(file_avg_damages, str(round(float(avg_damage), 2)))
        update_source_file(file_max_damages, str(round(float(max_damage), 2)))

    return

#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init():
    #   Create Settings Directory
    directory = os.path.join(os.path.dirname(__file__), "Settings")
    if not os.path.exists(directory):
        os.makedirs(directory)

    #   Load settings
    SettingsFile = os.path.join(os.path.dirname(__file__), "Settings\settings.json")
    global ScriptSettings
    ScriptSettings = MySettings(SettingsFile)
    
    # The destination directory has to exist
    if not os.path.isdir(ScriptSettings.FileDirectory):
        Parent.Log("PUBG Session Stats", "Path {} not found.".format(ScriptSettings.FileDirectory))
        sys.exit(1)

    # Setting the different files path
    global file_session_start
    file_session_start = ScriptSettings.FileDirectory + "\\" + conf.CONST_FILE_SESSION_START
    global file_games
    file_games = ScriptSettings.FileDirectory + "\\" + conf.CONST_FILE_GAMES
    global file_kills
    file_kills = ScriptSettings.FileDirectory + "\\" + conf.CONST_FILE_KILLS
    global file_wins
    file_wins = ScriptSettings.FileDirectory + "\\" + conf.CONST_FILE_WIN
    global file_assists
    file_assists = ScriptSettings.FileDirectory + "\\" + conf.CONST_FILE_ASSIST
    global file_dbno
    file_dbno = ScriptSettings.FileDirectory + "\\" + conf.CONST_FILE_DBNO
    global file_kd
    file_kd = ScriptSettings.FileDirectory + "\\" + conf.CONST_FILE_KD
    global file_kda
    file_kda = ScriptSettings.FileDirectory + "\\" + conf.CONST_FILE_KDA
    global file_top
    file_top = ScriptSettings.FileDirectory + "\\" + conf.CONST_FILE_TOP
    global file_avg_rank
    file_avg_rank = ScriptSettings.FileDirectory + "\\" + conf.CONST_FILE_AVG_RANK
    global file_total_damages
    file_total_damages = ScriptSettings.FileDirectory + "\\" + conf.CONST_FILE_TOTAL_DAMAGE
    global file_max_damages
    file_max_damages = ScriptSettings.FileDirectory + "\\" + conf.CONST_FILE_DAMAGE
    global file_avg_damages
    file_avg_damages = ScriptSettings.FileDirectory + "\\" + conf.CONST_FILE_AVG_DAMAGE


    # Set the local datetime in UTC
    local_tz = pytz.timezone (ScriptSettings.Timezone)
    dt_now_without_tz = DT.datetime.now()
    dt_now_with_tz = local_tz.localize(dt_now_without_tz, is_dst=None) # No daylight saving time
    dt_now_in_utc = dt_now_with_tz.astimezone(pytz.utc)

    update_source_file(file_session_start, dt_now_in_utc.strftime('%Y-%m-%d %H:%M:%S %Z'))
    
    init_data_files()

    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):

    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():

    global start

    try:
        start
    except NameError:
        start = time.time()

    current = time.time()
    elapsed = current - start

    # Parent.Log("PUBG Session Stats", str(current) + " --- " + str(start) + " --- " + str(current - start))

    if (elapsed > (ScriptSettings.Frequency * 60)):
        start = time.time()

        update_data()

    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters) 
#---------------------------
def Parse(parseString, userid, username, targetid, targetname, message):
    
    if "$myparameter" in parseString:
        return parseString.replace("$myparameter","I am a cat!")
    
    return parseString

#---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
#---------------------------
def ReloadSettings(jsonData):
    # Execute json reloading here
    ScriptSettings.__dict__ = json.loads(jsonData)
    ScriptSettings.Save(SettingsFile)
    return

#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    return