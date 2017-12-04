# installer for the blynkparse driver
# Copyright 2017 Laszlo Szucs

from setup import ExtensionInstaller

def loader():
    return BlynkParseInstaller()

class BlynkParseInstaller(ExtensionInstaller):
    def __init__(self):
        super(BlynkParseInstaller, self).__init__(
            version="0.1",
            name='blynkparse',
            description='Blynk parsing driver for weewx.',
            author="Laszlo Szucs",
            author_email="",
            config={
                'Station': {
                    'station_type': 'BlynkParse'},
                'BlynkParse': {
                    'poll_interval': '30',
                    'blynkurl': 'http://blynk-cloud.com/',
		        '[[blynk_map]]',
    			    'blynk_auth_code::blynk_pin=outTemp',
    			    'blynk_auth_code::blynk_pin=pressure',
                    'driver': 'user.blynkparse'}},
            files=[('bin/user', ['bin/user/blynkparse.py'])]
            )
