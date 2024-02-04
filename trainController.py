from itertools import cycle
from curio import sleep, Queue
from bricknil import attach, start
from bricknil.hub import DuploTrainHub
from bricknil.sensor import DuploTrainMotor, DuploSpeedSensor, DuploSpeaker, LED
from bricknil.const import Color
import logging
from inputs import get_gamepad

@attach(LED, name='led')
@attach(DuploSpeaker, name='speaker')
@attach(DuploTrainMotor, name='motor')
@attach(DuploSpeedSensor, name='speed_sensor', capabilities=['sense_speed', 'sense_count'])
class Train(DuploTrainHub):   
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.speed = 0

  async def speed_sensor_change(self):
    real_speed = self.speed_sensor.value[DuploSpeedSensor.capability.sense_speed]
    if real_speed < 20 and real_speed > -20 and self.speed != 0:
       self.speed = 0
       self.message("Obstructed, stopping")
       
  async def run(self):
      colors = cycle([Color.red, Color.purple, Color.yellow, Color.blue, Color.white])

      await self.motor.set_speed(self.speed)
      self.message("Running")
      while True:
        events = get_gamepad()
        for event in events:
            print(event.ev_type, event.code, event.state)
            if event.code == "ABS_Y" and event.state == 0:
              print("ramping up")
              if(self.speed == 0) : 
                self.speed = 50
              else : 
                self.speed = self.speed + 20
                if self.speed > 200 :
                  self.speed = 200
                if self.speed <= 50 and self.speed <= -50 : 
                   self.speed = 0

              await self.motor.ramp_speed(self.speed, 1000)
              await sleep(1)

            if event.code == "ABS_Y" and event.state == 255:
              if self.speed > 0 and self.speed < 50 :
                self.speed = 0
              else :
                if self.speed == 0 :
                   self.speed = -50
                else : 
                  self.speed = self.speed - 20
                  if self.speed <= -200 :
                     self.speed = 200
                  if self.speed <= 50 and self.speed <= -50 : 
                   self.speed = 0

              await self.motor.ramp_speed(self.speed, 1000)
              await sleep(1)
            
            if event.code == "BTN_THUMB" and event.state == 1:
               self.speed = 0
               await self.motor.set_speed(self.speed)
               await self.speaker.play_sound(DuploSpeaker.sounds.brake)
               await sleep(0.1)
            
            if event.code == "BTN_THUMB2" and event.state == 1:
               await self.speaker.play_sound(DuploSpeaker.sounds.horn)
               await sleep(0.1)

            if event.code == "BTN_PINKIE" and event.state == 1:
               await self.led.set_color(next(colors))
               await sleep(0.1)

            if event.code == "BTN_TOP2" and event.state == 1:
              await self.led.set_color(next(colors))
              await sleep(0.1)

async def system():
    train = Train('My train')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start(system)
    