import sakeclasses
import sakeconfig
import requests
import requests_cache
import asyncio
import aiohttp
requests_cache.install_cache(expire_after=65000)
mkl_region = {'0':'world', '1':'japan', '2':'americas', '3':'europe', '4':'oceania'}

mkl_course = {'8':"49", '1':"50", '2':"51", '4':"52", '0':"53", '5':"54", '6':"55", '7':"56", '9':"57", '15':"58", '3':"60", '11':"59", '10':"62", '14':"61", '12':"63", '13':"64", '16':"65", '20':"66", '25':"67", '26':"68", '27':"69", '31':"70", '23':"71", '18':"72", '21':"73", '30':"74", '29':"75", '17':"76", '24':"77", '22':"78", '19':"79", '28':"80"}


def parse_mkl_leaderboard(leaderboard_json):
    data = leaderboard_json['data']
    instances = []
    possible_chadsoft_urls = ['https://www.chadsoft' , 'http://chadsoft.co.u' , 'https://chadsoft.co.' , 'http://www.chadsoft.', 'chadsoft.co.uk/time-', 'www.chadsoft.co.uk/t']
    possible_discord_urls = ['https://cdn.discorda', 'cdn.discordapp.com/a', 'http://cdn.discord']
    possible_maschell_url1 = 'https://maschell.de/' 
    possible_maschell_url2 = 'http://maschell.de/g'
    possible_maschell_url3 = 'maschell.de/ghostdat'
    possible_ninrankings_url1 = 'https://ninrankings.'
    possible_ninrankings_url2 = 'http://ninrankings.o'
    possible_ninrankings_url3 = 'ninrankings.org/ghos'

    #creating a URL that requests can get a ghost from
    if not data[0]['ghost']:
        ghost_download = 'https://chadsoft.co.uk/time-trials/rkgd/80/4D/8CBC1D501585B48E8EAEC35DAE94B5FF8E37.html'
    elif data[0]['ghost'][:20] in possible_chadsoft_urls:
        ghost_download = data[0]['ghost'][:-4] + 'rkg'
    elif data[0]['ghost'][:20] in possible_discord_urls:
        ghost_download = data[0]['ghost']
    elif data[0]['ghost'][:20] == possible_maschell_url1:
        ghost_download = 'https://maschell.de/ghostdatabase/download.php?id=' + data[0]['ghost'][53:]
    elif data[0]['ghost'][:20] == possible_maschell_url2:
        ghost_download = 'https://maschell.de/ghostdatabase/download.php?id=' + data[0]['ghost'][52:]
    elif data[0]['ghost'][:20] == possible_maschell_url3:
        ghost_download = 'https://maschell.de/ghostdatabase/download.php?id=' + data[0]['ghost'][45:]
    elif data[0]['ghost'][:20] == possible_ninrankings_url1:
        ghost_download = 'https://ninrankings.org/ghostdatabase/download.php?id=' + data[0]['ghost'][57:]
    elif data[0]['ghost'][:20] == possible_ninrankings_url2:
        ghost_download = 'https://ninrankings.org/ghostdatabase/download.php?id=' + data[0]['ghost'][56:]
    elif data[0]['ghost'][:20] == possible_ninrankings_url3:
        ghost_download = 'https://ninrankings.org/ghostdatabase/download.php?id=' + data[0]['ghost'][49:]
    else:
        ghost_download = 'https://chadsoft.co.uk/time-trials/rkgd/80/4D/8CBC1D501585B48E8EAEC35DAE94B5FF8E37.html'

    print('Parsed download link for ghost request.')
    return ghost_download

async def download_ghost_to_server_as_bin(sake_params):
    print(sake_params)
    if len(sake_params) == 44:
        print('44')
        course_id = sake_params[9:-33]
        region_id = sake_params[-1]
    elif len(sake_params) == 43:
        print('43')
        course_id = sake_params[9:-33]
        region_id = sake_params[-1]
    elif len(sake_params) == 29:
        print('29')
        course_id = sake_params[9:-18]
        region_id = '0'
    elif len(sake_params) == 28:
        print('28')
        course_id = sake_params[9:-18]
        region_id = '0'
    else:
        raise Exception('RMCE sent invalid request.')

    print(course_id)
    print(region_id)
    course_url = f'https://www.mkleaderboards.com/api/charts/mkw_nonsc_{mkl_region[region_id]}/{mkl_course[course_id]}'
    lb_json = requests.get(course_url)
    print('Requested ghost. Waiting...')
    ghost = requests.get(parse_mkl_leaderboard(lb_json.json()))
    #ghost = requests.get('https://chadsoft.co.uk/time-trials/rkgd/B9/70/0892669A4B02FBCE4920AAEA01893B6F8741.rkg')
    with open('ghost.bin', 'wb+') as f:
        f.write(ghost.content)
        f.close()

    print('Downloaded ghost for retrieval by response server.')