#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  Copyright (C) 2015-2018 Shenzhen Auto-link world Information Technology Co., Ltd.
  All Rights Reserved

  Name: TBoxCore.py
  Purpose:

  Created By:    Clive Lau <liuxusheng@auto-link.com.cn>
  Created Date:  2018-01-11

  Changelog:
  Date         Desc
  2018-01-11   Created by Clive Lau
"""

# Builtin libraries
import os
import time
import shutil
import commands
from ConfigParser import ConfigParser

# Third-party libraries
from robot.api import logger

# Customized libraries
import Config as CONFIG
from MqttComm.MqttComm import MqttComm
from CanComm.CanComm import CanComm
from DesignPattern.Singleton import Singleton


class TBoxCore(Singleton):
    def __init__(self):
        self._tag = self.__class__.__name__ + ' '
        logger.info(self._tag + "__init__ called")
        # ini ConfigParse
        self._config = ConfigParser()
        self._config.read('config.ini')
        device = self._config.get('Device', 'device')
        server = self._config.get('MQTT', 'server')
        channel = self._config.get('PCAN', 'channel')
        baudrate = self._config.get('PCAN', 'baudrate')
        hwtype = self._config.get('PCAN', 'hwtype')
        ioport = self._config.get('PCAN', 'ioport')
        interrupt = self._config.get('PCAN', 'interrupt')
        # device = CONFIG.DEVICE
        # server = CONFIG.SERVER
        # channel = CONFIG.CHANNEL
        # baudrate = CONFIG.BAUDRATE
        # hwtype = CONFIG.HWTYPE
        # ioport = CONFIG.IOPORT
        # interrupt = CONFIG.INTERRUPT

        self._expected_device = device
        self._mqttc = MqttComm(device, server)
        self._pcan = CanComm(channel, baudrate, hwtype, ioport, interrupt)

    def __del__(self):
        logger.info(self._tag + "__del__ called")

    def on_create(self):
        logger.info(self._tag + "on_create called")
        # self._mqttc.on_response = self.on_response
        if not self._mqttc.on_create():
            return False
        if not self._pcan.on_create():
            return False
        return True

    def on_destroy(self):
        logger.info(self._tag + "on_destroy called")
        self._mqttc.on_destroy()
        self._pcan.on_destroy()

    @staticmethod
    def on_clean_log():
        commands.getstatusoutput('adb logcat -c -b mcu -b mpu -b system -b tsp')

    @staticmethod
    def get_special_log(path, obj):
        (status, output) = commands.getstatusoutput('adb logcat -d -b ' + obj)
        if not status:
            with open(path + '/' + obj + '.log', 'w') as f:
                f.write(output)

    @staticmethod
    def on_collect_log(path):
        try:
            os.makedirs(path)
        except OSError, e:
            logger.warn(str(e))
            # if e.errno == 17:
            #     shutil.rmtree(path)
            #     os.mkdir(path)
        TBoxCore.get_special_log(path, 'mcu')
        TBoxCore.get_special_log(path, 'mpu')
        TBoxCore.get_special_log(path, 'system')
        TBoxCore.get_special_log(path, 'tsp')

    def wait_until_ready(self):
        # count = 0
        # while count < 10:
        #     if self._mqttc.is_connected:
        #         return True
        #     time.sleep(1)
        #     count += 1
        # return False
        while not self._mqttc.is_connected:
            time.sleep(1)
        return True

    def on_request_remote_config(self, item, data, timeout):
        """
        """
        logger.info(self._tag + "on_request_remote_config called")
        return self._mqttc.on_request_remote_config(item, data, timeout)

    def on_request_can_config(self, item, data, timeout):
        """
        """
        logger.info(self._tag + "on_request_can_config called")
        return self._pcan.on_request(item, data)

    def on_request_can_data(self, item, timeout):
        """
        """
        logger.info(self._tag + "on_request_can_data called")
        return self._mqttc.on_request_can_data(item, timeout)


if __name__ == '__main__':
    pass
