import requests
import requests_cache
from bs4 import BeautifulSoup
from xml.dom import minidom
import os
import raceutil
import raceclasses
import raceconfig
import io
import time as execution_time

requests_cache.install_cache('mkl_cache', expire_after=1200)

async def create_top_10(request_data):

	#open the incoming request
	incoming_request = io.BytesIO(request_data)

	#write the request to a file, for many reasons including debugging and also for the sake of having a valid request handy
	request_tracker = open('last_request.xml', 'wb+')
	request_tracker.write(request_data)
	request_tracker.close()

	#parsing the rankings search parameters from the incoming request
	parameters = minidom.parse(incoming_request)
	course_id = parameters.getElementsByTagName('ns1:courseid')[0].firstChild.nodeValue
	region_id = parameters.getElementsByTagName('ns1:regionid')[0].firstChild.nodeValue

	if course_id <= 31: #normal 32 courses

		#mapping the values in the incoming requests to their mkl equivalent values
		course_url = []
		mkl_region = {'0':'world', '1':'japan', '2':'americas', '3':'europe', '4':'oceania'}
		mkl_course = {'8':"49", '1':"50", '2':"51", '4':"52", '0':"53", '5':"54", '6':"55", '7':"56", '9':"57", '15':"58", '3':"60", '11':"59", '10':"62", '14':"61", '12':"63", '13':"64", '16':"65", '20':"66", '25':"67", '26':"68", '27':"69", '31':"70", '23':"71", '18':"72", '21':"73", '30':"74", '29':"75", '17':"76", '24':"77", '22':"78", '19':"79", '28':"80", '390':'80'}
		course_url = f'https://www.mkleaderboards.com/api/charts/mkw_nonsc_{mkl_region[region_id]}/{mkl_course[course_id]}'

		#requesting and parsing data from mkl API
		print(f'Requesting leaderboard data for track {course_id} in region {region_id} from MKLeaderboards API ({course_url})...')
		res = requests.get(f'{course_url}')
		leaderboard_json = res.json(encoding='utf-8-sig')
		leader_board_data = raceutil.parse_mkl_leaderboard(leaderboard_json)
		pids = raceutil.return_pids(leaderboard_json)
		amount_of_records = len(pids)
		print('Parsed MKL Leaderboard Data.')

		#creating the xml document
		returned_packet = minidom.Document()
		returned_packet.toxml(encoding="UTF-8")
		xml = returned_packet.createElement('RankingDataResponse') #xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://gamespy.net/RaceService/"')
		xml.setAttribute('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
		xml.setAttribute('xmlns:xsd', "http://www.w3.org/2001/XMLSchema")
		xml.setAttribute('xmlns', "http://gamespy.net/RaceService/")
		returned_packet.appendChild(xml)
		responseCode = returned_packet.createElement('responseCode')
		responseCodeValue = returned_packet.createTextNode("0")
		responseCode.appendChild(responseCodeValue)
		xml.appendChild(responseCode)
		dataArray = returned_packet.createElement('dataArray')
		numrecords = returned_packet.createElement('numrecords')
		data = returned_packet.createElement('data')

		#add ghost urls to a list for async dl
		ghost_url_list = []
		for i in range(amount_of_records):
			ghost_url_list.append(leader_board_data[i].ghost_url)

		#asynchronously downloading the ghosts in order to help bypass the slowness of chadsoft
		print('Doing ghost downloads...')
		start_time = execution_time.time()
		ghosts = raceutil.asyncdownload(ghost_url_list)
		print(f'Ghost downloads complete. Took {execution_time.time() - start_time} seconds.' )
		#creating time data
		timevalues = []
		for ghost in leader_board_data:
			timevalue = returned_packet.createTextNode(f'{ghost.time}')
			timevalues.append(timevalue)

		#creating mii data aka userdata
		userdatas = []
		for i, ghost in enumerate(leader_board_data):

			encode = raceutil.create_base64_encode(ghosts[i], ghost.country, ghost.player_name, ghost.rank, ghost.time, ghost.printedtime, ghost.countryname)	
			userdatas.append(encode)

		#creating rankingdata, which is pid + rank + time + miidata
		rankingdatas = []
		for i in range(amount_of_records):
			RankingData = returned_packet.createElement('RankingData')
			ownerid = returned_packet.createElement('ownerid')
			owneridvalue = returned_packet.createTextNode(raceutil.match_pids(str(pids[i])))
			ownerid.appendChild(owneridvalue)
			rank = returned_packet.createElement('rank')
			rankValue = returned_packet.createTextNode(str(i))
			rank.appendChild(rankValue)
			userdata = returned_packet.createElement('userdata')
			userdataValue = returned_packet.createTextNode(str(userdatas[i])[2:-1])
			userdata.appendChild(userdataValue)
			time = returned_packet.createElement('time')
			time.appendChild(timevalues[i])
			RankingData.appendChild(ownerid)
			RankingData.appendChild(rank)
			RankingData.appendChild(time)
			RankingData.appendChild(userdata)
			rankingdatas.append(RankingData)

		#append all of the ranking data nodes to the main data node
		for i in range(amount_of_records):
			data.appendChild(rankingdatas[i])


		numrecordsValue = returned_packet.createTextNode(str(amount_of_records))
		numrecords.appendChild(numrecordsValue)
		dataArray.appendChild(numrecords)
		dataArray.appendChild(data)
		xml.appendChild(dataArray)
		xml_str = returned_packet.toxml(encoding="utf-8")

		#write the response to a file, for many reasons including debugging and also for the sake of having a valid response handy
		f = open('last_response.xml', 'wb+')
		f.write(xml_str)
		f.close()

		#send the xml to be returned to the client
		return xml_str

	elif course_id >= 32: #competition rankings request, repurposed for total time top 10
		
		incoming_request = io.BytesIO(request_data)

		request_tracker = open('last_request.xml', 'wb+')
		request_tracker.write(request_data)
		request_tracker.close()

		total_time_url = "https://www.mkleaderboards.com/mkw/totals/nonsc"

		print("requesting data for Total Time Top 10 From MKLeaderboards Website...")
		totalTimePage = requests.get(total_time_url).text
		html = BeautifulSoup(totalTimePage, 'html.parser')
		totalTimeTable = html.find("table")
		players = totalTimeTable.findAll("tr")
		pids = []
		flags = []
		times = []

		for i, player in enumerate(players):
			if i != 0 and i <=10: 
				data = player.findAll('td')
				flag = data[1].findAll('img')#[0]['src']
				for f in flag:
					flags.append(f['src'][-6:-4].upper())
				pid = data[2].findAll()
				for p in pid:
					pids.append(p['href'][43:])
				time = data[3].text#.findAll()
				times.append(time)

		ghosts = raceutil.asyncdownload(raceutil.get_fill_ins_from_mkl_pid(pids))

		userdatas = []

		for i, ghost in enumerate(ghosts):
			encode = raceutil.create_base64_encode(ghost, flags[i], "", channel_time_parse(times[i]), times[i], flag[i])


		rankingdatas = []
		for i in range(amount_of_records):
			RankingData = returned_packet.createElement('RankingData')
			ownerid = returned_packet.createElement('ownerid')
			owneridvalue = returned_packet.createTextNode(raceutil.match_pids(str(pids[i])))
			ownerid.appendChild(owneridvalue)
			rank = returned_packet.createElement('rank')
			rankValue = returned_packet.createTextNode(str(i))
			rank.appendChild(rankValue)
			userdata = returned_packet.createElement('userdata')
			userdataValue = returned_packet.createTextNode(str(userdatas[i])[2:-1])
			userdata.appendChild(userdataValue)
			time = returned_packet.createElement('time')
			time.appendChild(timevalues[i])
			RankingData.appendChild(ownerid)
			RankingData.appendChild(rank)
			RankingData.appendChild(time)
			RankingData.appendChild(userdata)
			rankingdatas.append(RankingData)

		#append all of the ranking data nodes to the main data node
		for i in range(amount_of_records):
			data.appendChild(rankingdatas[i])


		numrecordsValue = returned_packet.createTextNode(str(amount_of_records))
		numrecords.appendChild(numrecordsValue)
		dataArray.appendChild(numrecords)
		dataArray.appendChild(data)
		xml.appendChild(dataArray)
		xml_str = returned_packet.toxml(encoding="utf-8")

		#write the response to a file, for many reasons including debugging and also for the sake of having a valid response handy
		f = open('last_response.xml', 'wb+')
		f.write(xml_str)
		f.close()

		#send the xml to be returned to the client
		return xml_str
