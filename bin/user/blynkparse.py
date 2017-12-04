#!/usr/bin/python
#
# Copyright 2017 Laszlo Szucs
#
# weewx driver that reads data from a file
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.
#
# See http://www.gnu.org/licenses/


# This driver will read data from Blynk.  

#
# The units must be in the weewx.US unit system:
#   degree_F, inHg, inch, inch_per_hour, mile_per_hour
#
# To use this driver, put this file in the weewx user directory, then make
# the following changes to weewx.conf:
#
# [Station]
#     station_type = BlynkParse
# [BlynkParse]
#     poll_interval = 30          # number of seconds
#     blynkurl = http://blynk-cloud.com/     # location of data file
#     driver = user.blynkparse
#
# If the variables in the file have names different from those in the database
# schema, then create a mapping section called label_map.  This will map the
# variables in the file to variables in the database columns.  For example:
#
# [BlynkParse]
#     ...
#     [[blynk_map]]
#       blynk_auth_code::blynk_pin=outTemp
#    	blynk_auth_code::blynk_pin=pressure

from __future__ import with_statement
import syslog
import time
import urllib

import weewx.drivers

DRIVER_NAME = 'BlynkParse'
DRIVER_VERSION = "0.1"

def logmsg(dst, msg):
    syslog.syslog(dst, 'blynkparse: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

def _get_as_float(d, s):
    v = None
    if s in d:
        try:
            v = float(d[s])
        except ValueError, e:
            logerr("cannot get value for '%s': %s" % (s, e))
    return v

def loader(config_dict, engine):
    return BlynkParseDriver(**config_dict[DRIVER_NAME])

class BlynkParseDriver(weewx.drivers.AbstractDevice):
    """weewx driver that reads data from Blynk server"""

    def __init__(self, **stn_dict):
        # where to find the data file
        #self.path = stn_dict.get('path', '/var/tmp/wxdata')
        self.blynkurl = stn_dict.get('blynkurl', 'http://blynk-cloud.com/')

        # how often to poll the weather data file, seconds
        self.poll_interval = float(stn_dict.get('poll_interval', 30))
        # mapping from variable names to weewx names
        self.label_map = stn_dict.get('label_map', {})
	self.blynk_map = stn_dict.get('blynk_map', {})

        loginf("URL is %s" % self.blynkurl)
        loginf("polling interval is %s" % self.poll_interval)
        loginf('label map is %s' % self.label_map)
        loginf('Blynk map is %s' % self.blynk_map)

    def genLoopPackets(self):
        while True:
            # read whatever values we can get from the file
            data = {}
            try:

		for key in self.blynk_map:
		    loginf(key+ ' corresponds to '+ self.blynk_map[key])
		    auth_code,pin_name=key.split("::")
		    blynk_url = self.blynkurl + auth_code + "/get/" + pin_name
		    loginf("Blynk URL: " + blynk_url)
		    f = urllib.urlopen(blynk_url)
		    blynkdata = f.read()
		    value=blynkdata[2:(len(blynkdata)-2)]
		    name = self.blynk_map[key]
            data[name] = value
		    loginf(name + " = " + value)

            except Exception, e:
                logerr("read failed: %s" % e)

            # map the data into a weewx loop packet
            _packet = {'dateTime': int(time.time() + 0.5),
                       'usUnits': weewx.METRICWX}
            for vname in data:
                _packet[self.label_map.get(vname, vname)] = _get_as_float(data, vname)

            yield _packet
            time.sleep(self.poll_interval)

    @property
    def hardware_name(self):
        return "BlynkParse"

if __name__ == "__main__":
    import weeutil.weeutil
    driver = BlynkParseDriver()
    for packet in driver.genLoopPackets():
        print weeutil.weeutil.timestamp_to_string(packet['dateTime']), packet
