"""
Load balancer using asynchronous posting of https requests.

"""

import os
import time
from glob import glob

import aiohttp
import asyncio

import numpy as np

## Settings
url = "http://localhost:3001/"
dt = 0.1 # time between posted images
max_conn = 20 # Maximum allowed simultaneous connections
T = 2000 # Simulation time

# Need to supply the load generator with a data folder with images of faces to detect, 
# one example to use is the UMass face detection data set (http://vis-www.cs.umass.edu/fddb/)
data_path = "/home/ubuntu/application/data" 


async def postimage(session, url, path):
    file = {'file': open(path, "rb")}
    async with session.post(url, data=file) as response:
        r = await response.read()
        file['file'].close()

        if len(r) < 5000:
            print("Warning: No image recieved")

        return r

async def main(loop, url, image_paths, dt, T, max_conn):
    async with aiohttp.ClientSession() as session:
        tasks = set()
        kmax = len(image_paths)
        t0 = time.time()
        count = 0

        u = 0
        t = 0
        while time.time() - t0 < T:
            print("t: {}, T: {}, c: {}, u: {}".format(t, T, count, u))

            image_path = np.random.choice(image_paths)
            if len(tasks) >= max_conn:
                _done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            tasks.add(loop.create_task(postimage(session, url, image_path)))

            count += 1

            # P controller for driving latency compensation
            t = time.time()-t0
            e = (2+t/dt) - count
            u = 0.01*e

            time.sleep(max(dt - u, 0))

        await asyncio.wait(tasks)
        return tasks, count

image_paths =  []
for dir,_,_ in os.walk(data_path):
    image_paths.extend(glob(os.path.join(dir, "*.jpg")))

t0 = time.time()
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    t0 = time.time()
    tasks = loop.run_until_complete(main(loop, url, image_paths, dt, T, max_conn))
    print(time.time() - t0)
