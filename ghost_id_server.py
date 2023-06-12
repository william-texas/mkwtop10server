import asyncio
import io
import sys
import xml.dom
import logging
from xml.dom import minidom

import quart
from hypercorn.asyncio import serve
from hypercorn.config import Config
from quart import Quart
from quart import request

import racefunction
import sakeutil

config = Config()

app = Quart('server')


@app.route('/RaceService', methods=['POST'])
async def doNgTop10():
    print('Received Request For Top 10 Data...')
    request_data = await request.data
    response = await racefunction.create_top_10(request_data, True, request.remote_addr)
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


try:
    sys.argv[1]
    if sys.argv[1] == 'prod':
        config.bind = ["104.131.12.248:80"]  # at this ip address
except:
    config.bind = ["localhost:8000"]  # at this ip address
    asyncio.run(serve(app, config))
