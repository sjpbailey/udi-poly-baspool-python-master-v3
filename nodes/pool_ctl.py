
"""
Polyglot v3 node server
Copyright (C) 2021 Steven Bailey
MIT License
"""
import udi_interface
import sys
import time
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
from enum import Enum
import bascontrolns
from bascontrolns import Device, Platform

from nodes import pool_zone
#from nodes import irrigation_zone_1

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

class Controller(udi_interface.Node):
    id = 'ctl'
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
            {'driver': 'GV0', 'value': 0, 'uom': 56},
            ]

    def __init__(self, polyglot, parent, address, name):
        super(Controller, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0
        self.n_queue = []
        self.Parameters = Custom(polyglot, 'customparams')

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        polyglot.subscribe(polyglot.STOP, self.stop)
        polyglot.subscribe(polyglot.START, self.start, address)
        polyglot.subscribe(polyglot.ADDNODEDONE, self.node_queue)

        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    def parameterHandler(self, params):
        self.Parameters.load(params)
        validChildren = False

        if self.Parameters['nodes'] is not None:
            if int(self.Parameters['nodes']) > 0:
                validChildren = True
            else:
                LOGGER.error('Invalid number of nodes {}'.format(self.Parameters['nodes']))
        else:
            LOGGER.error('Missing number of node parameter')

        if validChildren:
            self.createChildren(int(self.Parameters['nodes']))
            self.poly.Notices.clear()
        else:
            self.poly.Notices['nodes'] = 'Please configure the number of child nodes to create.'

    def start(self):
        self.poly.setCustomParamsDoc()
        self.poly.updateProfile()

    # Class form bascontrolns
    class bc:
        def __init__(self, sIpAddress, ePlatform):
            self.bc = Device()
            self.ePlatform = ePlatform

    def get_request(self, url):
        try:
            r = requests.get(url, auth=HTTPBasicAuth)
            if r.status_code == requests.codes.ok:
                if self.debug_enable == 'True' or self.debug_enable == 'true':
                    print(r.content)

                return r.content
            else:
                LOGGER.error("BASpi6u6r.get_request:  " + r.content)
                return None

        except requests.exceptions.RequestException as e:
            LOGGER.error("Error: " + str(e))    

    def createChildren(self, how_many):
        # delete any existing nodes
        nodes = self.poly.getNodes()
        for node in nodes:
            if node != 'controller':   # but not the controller node
                self.poly.delNode(node)

        LOGGER.info('Creating {} Pool Nodes'.format(how_many))
        for i in range(0, how_many):
            address = 'zone_{}'.format(i)
            title = 'Pool {}'.format(i)            
            ip = self.Parameters.poolip_0
            LOGGER.info(ip)
            ip1 = self.Parameters.poolip_1  
            LOGGER.info(ip1)
            ip2 = self.Parameters.poolip_2
            LOGGER.info(ip2)
            ip3 = self.Parameters.poolip_3  
            LOGGER.info(ip3)
            ip4 = self.Parameters.poolip_4
            LOGGER.info(ip4)
            ip5 = self.Parameters.poolip_5  
            LOGGER.info(ip5)
            node = pool_zone.PoolNode(self.poly, self.address, address, title, ip, ip1, ip2, ip3, ip4, ip5, self.bc )
            self.poly.addNode(node)
            self.wait_for_node_done()
        
        self.setDriver('GV0', how_many, True, True)

    def stop(self):
        nodes = self.poly.getNodes()
        for node in nodes:
            if node != 'controller':   # but not the controller node
                nodes[node].setDriver('ST', 0, True, True)

        self.poly.stop()

    def noop(self, command):
        LOGGER.info('Discover not implemented')

    commands = {'DISCOVER': noop}
