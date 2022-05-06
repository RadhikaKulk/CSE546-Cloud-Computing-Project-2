#!/usr/bin/python
import picamera
from multiprocessing import Process
import base64
import json                    
import time
import requests

BUCKET = "s3://ccinputvideobucket/"

# function to send request to API gateway with the video file
def send_API_request(*args, **kwargs):
    file_h264 = kwargs['file_h264']
    VIDEO_NAME = kwargs['VIDEO_NAME']
    api = 'https://w97zrvuvtb.execute-api.us-east-1.amazonaws.com/dev/' +VIDEO_NAME
    # print("API:", api)

    # read the video file
    with open(file_h264, "rb") as f:
        vid_bytes = f.read()
    vid_b64 = base64.b64encode(vid_bytes).decode("utf8")
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    payload = json.dumps({"video": vid_b64, "other_key": "value"})
    
    # send the request to the API Gateway
    start_time = time.time()
    response = requests.post(api, data=payload, headers=headers)
    try:
        # get the response data
        data = response.json()     
        latency = time.time() - start_time
        # print the latency and result
        print("Latency: {:.2f} seconds. Response: {}".format(latency, data))            
    except requests.exceptions.RequestException:
        # Something went wrong, print the response
        print(response.text)


def main():
    processes = list()

    # start picamera recording
    with picamera.PiCamera() as camera:
        for filename in camera.record_sequence('/home/pi/Desktop/project/videos/clip%02d.h264' % i for i in range(5)):
            print('Recording to %s' % filename)
            # record 0.5 seconds video
            camera.wait_recording(0.5)
            # create process to send request to API gateway
            p1 = Process(
                        target=send_API_request,  
                        kwargs={'file_h264': filename, 'VIDEO_NAME':filename.split("/")[-1]}
            )
            p1.start()
            processes.append(p1)

    for index, proc in enumerate(processes):
        print("Got back from Process: ", index)
        proc.join()

if __name__ == '__main__':
   main()
