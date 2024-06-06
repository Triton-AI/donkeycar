# Donkeycar: a python self driving library


![Build Status](https://github.com/autorope/donkeycar/actions/workflows/python-package-conda.yml/badge.svg?branch=main)
![Lint Status](https://github.com/autorope/donkeycar/actions/workflows/superlinter.yml/badge.svg?branch=main)
![Release](https://img.shields.io/github/v/release/autorope/donkeycar)


[![All Contributors](https://img.shields.io/github/contributors/autorope/donkeycar)](#contributors-)
![Issues](https://img.shields.io/github/issues/autorope/donkeycar)
![Pull Requests](https://img.shields.io/github/issues-pr/autorope/donkeycar?)
![Forks](https://img.shields.io/github/forks/autorope/donkeycar)
![Stars](https://img.shields.io/github/stars/autorope/donkeycar)
![License](https://img.shields.io/github/license/autorope/donkeycar)

![Discord](https://img.shields.io/discord/662098530411741184.svg?logo=discord&colorB=7289DA)

Donkeycar is minimalist and modular self driving library for Python. It is
developed for hobbyists and students with a focus on allowing fast experimentation and easy
community contributions.

#### Quick Links
* [Donkeycar Updates & Examples](http://donkeycar.com)
* [Build instructions and Software documentation](http://docs.donkeycar.com)
* [Discord / Chat](https://discord.gg/PN6kFeA)

![donkeycar](https://github.com/autorope/donkeydocs/blob/master/docs/assets/build_hardware/donkey2.png)

#### Use Donkey if you want to:
* Make an RC car drive its self.
* Compete in self driving races like [DIY Robocars](http://diyrobocars.com)
* Experiment with autopilots, mapping computer vision and neural networks.
* Log sensor data. (images, user inputs, sensor readings)
* Drive your car via a web or game controller or RC controller.
* Leverage community contributed driving data.
* Use existing CAD models for design upgrades.

### Get driving.
After building a Donkey2 you can turn on your car and go to http://localhost:8887 to drive.

### Modify your cars behavior.
The donkey car is controlled by running a sequence of events

```python
#Define a vehicle to take and record pictures 10 times per second.

import time
from donkeycar import Vehicle
from donkeycar.parts.cv import CvCam
from donkeycar.parts.tub_v2 import TubWriter
V = Vehicle()

IMAGE_W = 160
IMAGE_H = 120
IMAGE_DEPTH = 3

#Add a camera part
cam = CvCam(image_w=IMAGE_W, image_h=IMAGE_H, image_d=IMAGE_DEPTH)
V.add(cam, outputs=['image'], threaded=True)

#warmup camera
while cam.run() is None:
    time.sleep(1)

#add tub part to record images
tub = TubWriter(path='./dat', inputs=['image'], types=['image_array'])
V.add(tub, inputs=['image'], outputs=['num_records'])

#start the drive loop at 10 Hz
V.start(rate_hz=10)
```

See [home page](http://donkeycar.com), [docs](http://docs.donkeycar.com)
or join the [Discord server](http://www.donkeycar.com/community.html) to learn more.

# Running 3 Image DonkeyCar

1. **Connect to ‘UCSDRoboCar’ WiFi**
2. 

```bash
ssh jetson@ucsd-yellow.local
```

3. 

```bash
pwd: jetsonucsd
```

4. 

```bash
cd projects/icra_devel
```

5. 

```bash
bash run.sh
```

**If it says ‘docker already running’, do:**

```bash
docker stop donkey
```

6. 

```bash
source_donkey
```

7. 

```bash
cd..
```

8.

```bash
cd donkeycar
```

9.

```bash
git checkout
```

10.

```bash
git pull
```

11.

```bash
git checkout new-3image_donkey
```

12.

```bash
cd..
```

13.

```bash
cd mycars/3image
```

**To collect new data:**

1.

```bash
rm -r data
```

2.

```bash
python manage.py drive
```

**Data folder needs at least 5000~ images to deploy successfully, then:**

1.

```bash
python train.py --tub home/projects/mycars/3image home/projects/mycars/3image/data --model=models/{Insert whatever you want to name your model}.h5
```

**To deploy:**

1.

```bash
python manage.py drive --model=./models/{What you named your model}.h5
```

1. **Go to http://ucsd-yellow.local:8887/drive, switch (M)ode from (U)ser to Full (A)uto**

**How to run image augmentation code:**

1. **Navigate to the ‘3image’ folder**
2. **If [augment.py](http://augment.py) is not in the ‘3image’ folder, run:**

```bash
cp ../../donkeycar/donkeycar/templates/augment.py .
```

1. **Run:**

```bash
python augment.py --skew --flip --jitter --cutout
```
