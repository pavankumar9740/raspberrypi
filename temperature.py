from base64 import b64encode, b64decode
from hashlib import sha256
from urllib import quote_plus, urlencode
from hmac import HMAC
import requests
import json
import os
import time
import RPi.GPIO as GPIO
import dht11
import time

# Azure IoT Hub
URI = 'IOTRaspberry.azure-devices.net'
KEY = 'fbztdGbVtj9MmwhW+q7cKVb3Jzn6XHxR+91hJGCVS+A='
IOT_DEVICE_ID = 'mypi'
POLICY = 'iothubowner'


def generate_sas_token():
    expiry = 3600
    ttl = time.time() + expiry
    sign_key = "%s\n%d" % ((quote_plus(URI)), int(ttl))
    signature = b64encode(HMAC(b64decode(KEY), sign_key, sha256).digest())

    rawtoken = {
        'sr': URI,
        'sig': signature,
        'se': str(int(ttl))
    }

    rawtoken['skn'] = POLICY

    return 'SharedAccessSignature ' + urlencode(rawtoken)

def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    instance = dht11.DHT11(pin=17)
    token = generate_sas_token()

    while True:
        result=instance.read()
        if result.is_valid():
            
            message = {"temp":str(result.temperature),"humid":str(result.humidity),"deviceid":1}
            
            data = json.dumps(message)
            print(data)
            send_message(token, message)
            time.sleep(300)
            
def send_message(token, message):
    
    url = 'https://{0}/devices/{1}/messages/events?api-version=2016-11-14'.format(URI, IOT_DEVICE_ID)
    headers = {
    "Content-Type": "application/json",
    "Authorization": token
    }
    data = json.dumps(message)
    response = requests.post(url, data=data, headers=headers)

if __name__ == '__main__':
    
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup() 

        
        

