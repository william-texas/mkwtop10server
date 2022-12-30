from quart import Quart
from quart import request
import quart
from hypercorn.config import Config
from hypercorn.asyncio import serve
import raceutil
import racefunction
import raceclasses
import aiohttp
import asyncio
import sakeutil
import binascii
import io
import sys

config = Config()

app = Quart('server')


@app.route('/RaceService', methods=['POST'])
async def doNgTop10():
    print('Received Request For Top 10 Data...')
    request_data = await request.data
    response = await racefunction.create_top_10(request_data, True)
    print('Response Sent.')
    return response


@app.route('/RaceService2', methods=['POST'])
async def doScTop10():
    print('Received Request For Top 10 Data...')
    request_data = await request.data
    response = await racefunction.create_top_10(request_data, False)
    print('Response Sent.')
    return response


@app.route('/SakeGhostService', methods=['GET'])
async def send_ghost():
    print('Received Request For Ghost Data...')
    print('Sent ghost.')
    return await quart.send_file('ghost.bin', as_attachment=True)


@app.route('/SakeIDService', methods=['POST'])
async def do_parseghost_request():
    print('Received Request For Ghost Data...')

    with open('ghostID.xml', 'rb') as header:
        incoming_request = await request.data
        params = minidom.parse(io.BytesIO(incoming_request))
        sakesearchparams = params.getElementsByTagName('ns1:filter')[0].firstChild.nodeValue
        await sakeutil.download_ghost_to_server_as_bin(sakesearchparams)
        response = await quart.make_response(header.read())
        return response

        response.headers['Content-Disposition'] = 'attachment; filename=ghost.bin'
        response.headers['Sake-File-Result'] = '0'
        response.headers['Content-Type'] = 'application/octet-stream'
        '''
        sakesearchparams = params.getElementsByTagName('ns1:filter')[0].firstChild.nodeValue
        print(sakesearchparams)
        print(len(sakesearchparams))
        parsed = (sakesearchparams.replace(' and ', '\n')).splitlines()

        print(parsed)
        if len(parsed) == 3:
            sake_id = (parsed[0]).replace('course = ', '') + (parsed[2].replace('region = ', ''))
            return sake_id
        elif len(parsed) == 2:
            sake_id = (parsed[0]).replace('course = ', '') + '0'
            return sake_id
        else:
            sake_id = 1234 #returns this if the request is not from mario kart wii
            return sake_id
        '''


'''
		returned_packet = minidom.Document()
		returned_packet.toxml(encoding="UTF-8")
		soapenv = returned_packet.createElement('soap:Envelope')
		soapbody = returned_packet.createElement('soap:Body')
		seapenv.appendChild(soapbody)
		saerchforrecordsresponse = returned_packet.createElement('SearchForRecordsResponse')
		soapbody.appendChild(SearchForRecordsResponse)
		searchforrecordsresult = returned_packet.createElement('searchforrecordsresult')
		'''
'''
		returned_packet = minidom.parse(header.read())
		returned_packet.getElementsByTagName('intValue')[0].childNodes[0].nodeValue  = sake_id
		response = await quart.make_response(returned_packet)
		response.headers['Content-Disposition'] = 'attachment; filename=ghost.bin'
		response.headers['Sake-File-Result'] = '0'
		response.headers['Content-Type'] = 'application/octet-stream'
		print(response)
		return response

		'''

'''
'''

try:
    sys.argv[1]
    if sys.argv[1] == 'prod':
        config.bind = ["104.131.12.248:80"]  # at this ip address
except:
    config.bind = ["localhost:8000"]  # at this ip address
    asyncio.run(serve(app, config))
