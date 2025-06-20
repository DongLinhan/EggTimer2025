#### #### #### #### MozzieMonitor #### #### #### ####
#### Linhan Dong, Duvall Lab, Columbia Unversity ####
# Version hostory:
# 111023: basic preview and picture taking function with 1 min / pic frquency
# 111223: updated: more commandline real-time information; recording time
#         control, and pic_name reflects start recording time. 000000 marks
#         first picture at start time.
# 070524: MB2 with light control - first draft



#from picamera2.encoders import H264Encoder, Quality
from picamera2 import Picamera2, Preview
from libcamera import controls
import datetime
import time
import os
import RPi.GPIO as GPIO

#general inputs
experiment_name = 'OV003_112224_LVP_ZT0' # specify genotype and entrainment etc
recording_start_hour = 9 # in 24 hour time format
transition_duration = 30
ZT0 = 9
initial_light = True 

#cycle 1
cycle1 = True
cycle1_duration = 5
cycle1_type = 'LD' #'LD', 'DD', or 'LL'
cycle1_light_on = 9
cycle1_light_off = 21

#cycle 2
cycle2 = False
cycle2_duration = 0
cycle2_type = 'DD' #'LD', 'DD', or 'LL'
cycle2_light_on = 8
cycle2_light_off = 20

#cycle 3
cycle3 = False
cycle3_duration = 0
cycle3_type = 'LL' #'LD', 'DD', or 'LL'
cycle3_light_on = 8
cycle3_light_off = 20


#Light control parameters
pin = 12
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT)
pwm = GPIO.PWM(pin, 1000)

#light control function
def autopilot_light():
    global cycle1_active, cycle2_active, cycle3_active
    global cycle1_type, cycle2_type, cycle3_type
    global cycle1_light_on, cycle1_light_off, cycle2_light_on, cycle2_light_off, cycle3_light_on, cycle3_light_off 
    global transition_duration
    if cycle1_active and cycle1_type == 'LD':
        if datetime.datetime.now().hour == cycle1_light_on:
            duty_cycle = datetime.datetime.now().minute/transition_duration * 100
            if duty_cycle >= 100:
                duty_cycle = 100
            pwm.ChangeDutyCycle(duty_cycle)
            
        if datetime.datetime.now().hour == cycle1_light_off:
            duty_cycle = 100 - (datetime.datetime.now().minute/transition_duration * 100)
            if duty_cycle <= 0:
                duty_cycle = 0
            pwm.ChangeDutyCycle(duty_cycle)

        
    if cycle2_active and cycle2_type == 'LD':
        if datetime.datetime.now().hour == cycle2_light_on:
            duty_cycle = datetime.datetime.now().minute/transition_duration * 100
            if duty_cycle >= 100:
                duty_cycle = 100
            pwm.ChangeDutyCycle(duty_cycle)
            
        if datetime.datetime.now().hour == cycle2_light_off:
            duty_cycle = 100 - (datetime.datetime.now().minute/transition_duration * 100)
            if duty_cycle <= 0:
                duty_cycle = 0
            pwm.ChangeDutyCycle(duty_cycle)
            
    if cycle3_active and cycle3_type == 'LD':
        if datetime.datetime.now().hour == cycle3_light_on:
            duty_cycle = datetime.datetime.now().minute/transition_duration * 100
            if duty_cycle >= 100:
                duty_cycle = 100
            pwm.ChangeDutyCycle(duty_cycle)
            
        if datetime.datetime.now().hour == cycle3_light_off:
            duty_cycle = 100 - (datetime.datetime.now().minute/transition_duration * 100)
            if duty_cycle <= 0:
                duty_cycle = 0
            pwm.ChangeDutyCycle(duty_cycle)
            
                
    if cycle1_active and cycle1_type == 'DD':
        pwm.ChangeDutyCycle(0)
        
    if cycle1_active and cycle1_type == 'LL':
        pwm.ChangeDutyCycle(100)
        
    if cycle2_active and cycle2_type == 'DD':
        pwm.ChangeDutyCycle(0)
        
    if cycle2_active and cycle2_type == 'LL':
        pwm.ChangeDutyCycle(100)
    
    if cycle3_active and cycle3_type == 'DD':
        pwm.ChangeDutyCycle(0)
        
    if cycle3_active and cycle3_type == 'LL':
        pwm.ChangeDutyCycle(100)
            

#internal parameters - do not change
min_counter = 61 
hour_counter = 25
hour_elapsed = -1
cycle1_active = True
cycle2_active = False
cycle3_active = False
cycle_number = 0
experiment_duration = (cycle1_duration + cycle2_duration + cycle3_duration + 1) * 24

# Preview
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration()
picam2.configure(preview_config)
picam2.options["quality"] = 95
picam2.start_preview(Preview.QT)
picam2.start()
picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 15.0})
pause = input('Press Enter to end preview and continue')
picam2.stop_preview()
picam2.stop()

#parameters derived from inputs:
output_dir = ('/media/pi/KINGSTON/' + experiment_name)
os.mkdir(output_dir)

if recording_start_hour > datetime.datetime.now().hour:
    wait_hour = recording_start_hour - datetime.datetime.now().hour - 1
    wait_minute = (60 - datetime.datetime.now().minute) + (wait_hour * 60)
    pic_counter = 0 - wait_minute
elif recording_start_hour < datetime.datetime.now().hour:
    wait_hour = recording_start_hour + (23 - datetime.datetime.now().hour)
    wait_minute = (60 - datetime.datetime.now().minute) + (wait_hour * 60)
    pic_counter = 0 - wait_minute
elif recording_start_hour == datetime.datetime.now().hour:
    print("Warning: the hour to start recording is same as the hour right now - recording will proceed with first pic named 000000")
    pic_counter = 0


#Taking 1 pic / min until hours_elapsed = experiment duration

# first: initiaizing light condition
if initial_light:
    pwm.start(100)
else:
    pwm.start(0)

while hour_elapsed < experiment_duration:

    if min_counter != datetime.datetime.now().minute:
        if datetime.datetime.now().minute == 0 and datetime.datetime.now().hour == ZT0:
            cycle_number = cycle_number + 1
            if cycle_number > cycle1_duration:
                cycle1_active = False
                cycle2_active = True
                cycle3_active = False
                
            if cycle_number > (cycle1_duration + cycle2_duration):
                cycle1_active = False
                cycle2_active = False
                cycle3_active = True
            
        autopilot_light()
        print(datetime.datetime.now())
        print("we are in cycle " + str(cycle_number))
        print ("Taking picture #" + str(pic_counter) + " now")
        image_name = os.path.join(output_dir, '{:06d}.jpg'.format(pic_counter))
        still_config = picam2.create_still_configuration({"size" : (1200, 800)})
        picam2.configure(still_config)
        picam2.start()
        time.sleep(2) #warm up camera for 2 secs
        picam2.capture_file(image_name)
        picam2.stop()
        pic_counter = pic_counter + 1
        min_counter = datetime.datetime.now().minute
        
        
    if hour_counter != datetime.datetime.now().hour:
        hour_counter = datetime.datetime.now().hour
        hour_elapsed = hour_elapsed + 1
        print ("This is a new hour. It has been " + str(hour_elapsed) + " / " + str(experiment_duration) + " hours of recording" )

                
        