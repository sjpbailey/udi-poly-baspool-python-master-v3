"""
Polyglot v3 node server
Copyright (C) 2021 Steven Bailey
MIT License
"""
import udi_interface
import sys
import time
import urllib3
import asyncio
from bascontrolns import Device, Platform

LOGGER = udi_interface.LOGGER


class PoolNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, ip, ip1, ip2, ip3, ip4, ip5, bc):
        super(PoolNode, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.lpfx = '%s:%s' % (address, name)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        self.bc = bc
        LOGGER.info(address)
        # IP Address Sorter
        if address == 'zone_{}'.format(0):
            self.ipaddress = ip
        elif address == 'zone_{}'.format(1):
            self.ipaddress = ip1
        elif address == 'zone_{}'.format(2):
            self.ipaddress = ip2
        elif address == 'zone_{}'.format(3):
            self.ipaddress = ip3
        elif address == 'zone_{}'.format(4):
            self.ipaddress = ip4
        elif address == 'zone_{}'.format(5):
            self.ipaddress = ip5
        else:
            pass

    def start(self):
        if self.ipaddress is not None:
            # Which Device is installed BASpi-Edge-6u6r or BASpi-6u6r
            self.bc = Device(self.ipaddress)
            if self.bc.ePlatform == Platform.BASC_NONE:
                LOGGER.info('Unable to connect')
            elif self.bc.ePlatform == Platform.BASC_PI:
                LOGGER.info('connected to BASpi6U6R')
            elif self.bc.ePlatform == Platform.BASC_ED:
                LOGGER.info('connected to BASpi-Edge-6U6R Module ONE')
                LOGGER.info(str(self.bc.uiQty) +
                            ' Universal inputs in this BASpi Pool')
                LOGGER.info(str(self.bc.boQty) +
                            ' Binary outputs in this BASpi Pool')
                LOGGER.info("BASpiPool IO Points configured")
            else:
                pass

            # Input Output Status
            # Universal Inputs Status
            LOGGER.info("OSA: " + str(self.bc.universalInput(1)))
            LOGGER.info("POOL: " + str(self.bc.universalInput(2)))
            LOGGER.info("HEAT: " + str(self.bc.universalInput(3)))
            LOGGER.info("SOLAR: " + str(self.bc.universalInput(4)))
            LOGGER.info("FILTER PSI: " + str(self.bc.universalInput(5)))
            LOGGER.info("PUMP STATUS: " + str(self.bc.universalInput(6)))

            # Binary/Digital Outputs Status
            LOGGER.info("Valve Skim: " + str(self.bc.binaryOutput(1)))
            LOGGER.info("Valve Sweep: " + str(self.bc.binaryOutput(2)))
            LOGGER.info("Heat: " + str(self.bc.binaryOutput(3)))
            LOGGER.info("Light: " + str(self.bc.binaryOutput(4)))
            LOGGER.info("High Speed: " + str(self.bc.binaryOutput(5)))
            LOGGER.info("Low Speed: " + str(self.bc.binaryOutput(6)))

        ### Universal Inputs ###
        self.setInputDriver('GV0', 1)
        self.setInputDriver('GV1', 2)
        self.setInputDriver('GV2', 3)
        self.setInputDriver('GV3', 4)
        self.setInputDriver('GV4', 5)
        self.setInputDriver('GV5', 6)

    ### Universal Input Conversion ###
    def setInputDriver(self, driver, iIndex):
        input_val = self.bc.universalInput(iIndex)
        count = 0
        if input_val is not None:
            count = int(float(input_val))
            self.setDriver(driver, count)
        else:
            return

        ### Binary/Digital Outputs ###
        self.setOutputDriver('GV6', 1)
        self.setOutputDriver('GV7', 2)
        self.setOutputDriver('GV8', 3)
        self.setOutputDriver('GV9', 4)
        self.setOutputDriver('GV10', 5)
        self.setOutputDriver('GV11', 6)

    ### Binary Output Conversion ###
    def setOutputDriver(self, driver, input):
        output_val = self.bc.binaryOutput(input)
        count = 0
        if output_val is not None:
            count = (output_val)
            self.setDriver(driver, count)
        else:
            return
        pass

    # Pump Speed Control HIGH OFF LOW
    def pumpSpd(self, command):
        # self.pumpOn = int(command.get('value',))
        GV13 = int(command.get('value',))
        if GV13 == 1:
            self.bc.binaryOutput(5, 0)
            self.bc.binaryOutput(6, 0)
            self.setDriver("GV13", 1)
            LOGGER.info('Pump Off')
        elif GV13 == 0:
            self.bc.binaryOutput(5, 1)
            self.bc.binaryOutput(6, 0)
            self.setDriver("GV13", 0)
            LOGGER.info('Pump High Speed On')
        elif GV13 == 2:
            self.bc.binaryOutput(5, 0)
            self.bc.binaryOutput(6, 1)
            self.setDriver("GV13", 2)
            LOGGER.info('Pump Low Speed On')
        else:
            pass

    # Valve Control SKIM OFF SWEEP
    def cmdVlv(self, command):
        # self.valveOn = int(command.get('value',))
        GV14 = int(command.get('value',))
        if GV14 == 1:
            self.bc.binaryOutput(1, 0)
            self.bc.binaryOutput(2, 0)
            self.setDriver("GV14", 1)
            LOGGER.info('Valve Stop')
        elif GV14 == 0:
            self.bc.binaryOutput(1, 1)
            self.bc.binaryOutput(2, 0)
            self.setDriver("GV14", 0)
            LOGGER.info('Valve Skim')
        elif GV14 == 2:
            self.bc.binaryOutput(2, 1)
            self.bc.binaryOutput(1, 0)
            self.setDriver("GV14", 2)
            LOGGER.info('Valve Sweep')
        else:
            pass

    # Pool Light
    def cmdSolar(self, command):
        self.setsolar = int(command.get('value'))
        self.setDriver("GV15", self.setsolar)
        self.setsolar = int(command.get('value',))
        if self.setsolar == 1:
            self.bc.binaryOutput(4, 1)
            self.setDriver("GV15", 1)
            LOGGER.info('Light On')
        elif self.setsolar == 0:
            self.bc.binaryOutput(4, 0)
            self.setDriver("GV15", 0)
            LOGGER.info('Light Off')
        else:
            pass

    # Boiler Heat
    def cmdBoiler(self, command):
        self.setboiler = int(command.get('value'))
        self.setDriver("GV16", self.setboiler)
        self.setboiler = int(command.get('value',))
        if self.setboiler == 1:
            if self.bc.binaryOutput(5) or self.bc.binaryOutput(6) and self.setInputDriver(6) == 1:
                self.bc.binaryOutput(3, 1)
                self.setDriver("GV16", 1)
                LOGGER.info('Heat Auto')
        elif self.setboiler == 0:
            self.bc.binaryOutput(3, 0)
            self.setDriver("GV16", 0)
            LOGGER.info('Heat Disabled')
        else:
            pass

    def poll(self, polltype):
        if 'longPoll' in polltype:
            LOGGER.debug('longPoll (node)')
        else:
            self.start()
            LOGGER.debug('shortPoll (node)')

    def query(self, command=None):
        self.start()
        LOGGER.info(self.bc)

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2},
        {'driver': 'GV0', 'value': 1, 'uom': 17},
        {'driver': 'GV1', 'value': 1, 'uom': 17},
        {'driver': 'GV2', 'value': 1, 'uom': 17},
        {'driver': 'GV3', 'value': 1, 'uom': 17},
        {'driver': 'GV4', 'value': 1, 'uom': 52},
        {'driver': 'GV5', 'value': 1, 'uom': 80},
        {'driver': 'GV6', 'value': 1, 'uom': 80},
        {'driver': 'GV7', 'value': 1, 'uom': 80},
        {'driver': 'GV8', 'value': 1, 'uom': 80},
        {'driver': 'GV9', 'value': 1, 'uom': 80},
        {'driver': 'GV10', 'value': 0, 'uom': 80},
        {'driver': 'GV11', 'value': 0, 'uom': 80},
        {'driver': 'GV13', 'value': 1, 'uom': 25},
        {'driver': 'GV14', 'value': 1, 'uom': 25},
        {'driver': 'GV15', 'value': 0, 'uom': 25},
        {'driver': 'GV16', 'value': 0, 'uom': 25},

    ]

    id = 'zone'

    commands = {
        'PAON': pumpSpd,
        'PBON': cmdVlv,
        'PCON': cmdSolar,
        'PDON': cmdBoiler,
        'PING': query
    }
