import base64
from multiprocessing.dummy import Pool as ThreadPool

import requests
import requests_cache
from tinydb import TinyDB, Query

import raceclasses
from mkw_ghosts import MkwGhosts

requests_cache.install_cache('ghost_cache', allowable_codes=(200,), backend='sqlite', expire_after=-1)
User = Query()
controller_id_dict = {'Controllers.wii_remote': 1, 'Controllers.wii_wheel': 0, 'Controllers.gamecube_controller': 2,
                      'Controllers.classic_controller': 3}


# custom prefix request
def do_download(url):
    data = requests.get(url)
    return data.content


def asyncdownload(ghost_url_list):
    pool = ThreadPool(10)
    results = pool.map(do_download, ghost_url_list)
    ghosts = []
    for result in results:
        ghosts.append(result)
    return ghosts


def match_pids(mkl_pid):
    pid_db = TinyDB('pids.json')
    query_object = Query()

    existing_data = pid_db.search(query_object.mkl_pid == mkl_pid)

    if existing_data == []:
        return '600000000'
    else:
        entry = (pid_db.search(User.mkl_pid == mkl_pid)[0])
        return str(entry['Wiimmfi_pid'])


def return_pids(leaderboard_json):
    records = leaderboard_json['data']
    pids = []
    for data in records:
        pids.append(data['player_id'])
    return pids


def create_base64_encode(ghostdata, country, player_name, rank, time, printedtime, countryname):
    kaitai = MkwGhosts.from_bytes(ghostdata)
    f = open(f'rank{rank}rkg.rkg', 'wb+')
    f.write(ghostdata)
    miidata = bytearray()
    mii = bytes(kaitai.driver_mii_data)
    miidata += mii
    crc_16 = (kaitai.crc16_mii).to_bytes(2, 'big')  # leaving out the to_bytes() function will make mkw crash
    miidata += crc_16
    controllerdata = controller_id_dict.get(str(kaitai.controller_id), 3)
    miidata += controllerdata.to_bytes(1, "big")
    unknown = chr(0)
    miidata += bytes(unknown, 'utf8')
    region = (kaitai.region_code).to_bytes(1, 'big')
    miidata += region
    location = bytes([country])
    miidata += location
    encode = base64.b64encode(bytearray(miidata))
    print(
        f'Finished creating leaderboard element for player {player_name} ({rank}), from {countryname}, finishing in {printedtime}, with controller {str(kaitai.controller_id)}')
    f.close()
    return encode


def parse_mkl_leaderboard(leaderboard_json):
    fill_in_db = TinyDB('fill_ins.json')
    records = leaderboard_json['data']
    instances = []
    ghost_fill_ins = fill_in_db
    possible_chadsoft_urls = ['https://www.chadsoft', 'http://chadsoft.co.u', 'https://chadsoft.co.',
                              'http://www.chadsoft.', 'chadsoft.co.uk/time-', 'www.chadsoft.co.uk/t']
    possible_discord_urls = ['https://cdn.discorda', 'cdn.discordapp.com/a', 'http://cdn.discord']
    possible_maschell_url1 = 'https://maschell.de/'
    possible_maschell_url2 = 'http://maschell.de/g'
    possible_maschell_url3 = 'maschell.de/ghostdat'
    possible_ninrankings_url1 = 'https://ninrankings.'
    possible_ninrankings_url2 = 'http://ninrankings.o'
    possible_ninrankings_url3 = 'ninrankings.org/ghos'

    i = 0
    for data in records:
        # creating a URL that requests can get a ghost from
        if not data['ghost']:
            playerid = data['player_id']
            name = data['name']
            existing_data = fill_in_db.search(User.mkl_pid == playerid)
            if existing_data != []:
                print(f'Filled in Mii for ID: {str(playerid)} ({name})')
                ghost_download = (existing_data[0])['download_link']
            else:
                print(f'No fill in available for ID: {str(playerid)} ({name})')
                ghost_download = 'https://cdn.discordapp.com/attachments/456603906785411072/833075555112321104/noghost.rkg'
            '''
            if playerid in ghost_fill_ins.keys():
                ghost_download = ghost_fill_ins[playerid]
                print(f'Filled in Mii for ID: {str(playerid)} ({name})')
            else:
                print(f'No fill in available for ID: {str(playerid)} ({name})')
                ghost_download = 'https://cdn.discordapp.com/attachments/456603906785411072/833075555112321104/noghost.rkg'
            '''
        elif data['ghost'][:20] in possible_chadsoft_urls:
            ghost_download = data['ghost'][:-4] + 'rkg'
        elif data['ghost'][:20] in possible_discord_urls:
            ghost_download = data['ghost']
        elif data['ghost'][:20] == possible_maschell_url1:
            ghost_download = 'https://maschell.de/ghostdatabase/download.php?id=' + data['ghost'][53:]
        elif data['ghost'][:20] == possible_maschell_url2:
            ghost_download = 'https://maschell.de/ghostdatabase/download.php?id=' + data['ghost'][52:]
        elif data['ghost'][:20] == possible_maschell_url3:
            ghost_download = 'https://maschell.de/ghostdatabase/download.php?id=' + data['ghost'][45:]
        elif data['ghost'][:20] == possible_ninrankings_url1:
            ghost_download = 'https://ninrankings.org/ghostdatabase/download.php?id=' + data['ghost'][57:]
        elif data['ghost'][:20] == possible_ninrankings_url2:
            ghost_download = 'https://ninrankings.org/ghostdatabase/download.php?id=' + data['ghost'][56:]
        elif data['ghost'][:20] == possible_ninrankings_url3:
            ghost_download = 'https://ninrankings.org/ghostdatabase/download.php?id=' + data['ghost'][49:]
        else:
            ghost_download = 'https://cdn.discordapp.com/attachments/456603906785411072/833075555112321104/noghost.rkg'

        instances.append(raceclasses.Ghost(data['name'], data['score'], ghost_download, data['rank'], data['country'],
                                           data['score_formatted']))

        i += 1
    return instances


def get_fill_ins_from_mkl_pid(pids):
    ghosts = []
    fill_in_db = TinyDB('fill_ins.json')
    for pid in pids:
        existing_data = fill_in_db.search(User.mkl_pid == int(pid))
        if existing_data != []:
            ghost_download = (existing_data[0])['download_link']
        else:
            ghost_download = 'https://cdn.discordapp.com/attachments/456603906785411072/833075555112321104/noghost.rkg'
        ghosts.append(ghost_download)
    return ghosts


def channel_time_parse(time):
    minutes = int(time[0:2]) * 60000
    seconds = int(time[3:5]) * 1000
    milliseconds = int(time[6:])

    total = minutes + seconds + milliseconds
    return total


def match_flag_with_country_code(flag):
    return raceclasses.country_table[flag]
