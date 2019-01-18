"""
    example program for ivi library implemented features for the n6700B power supply mainframe

	write driverr for hp/agilent n6700b power supply
		- model after rogol tri output psu driver?
		- cmd line interface for jay?
		- make example programm
		        y- done
			    y- reset
			    y- talk over usb, tcp, gpib?
			- set all channels, set foldback move, cc/cv, max v/I
			x- configure 2 parellel modules as 1 channel
			    y- set display to cnallel value or meter view (meter view default in remote mode)
			~- set/ read gpio?
			- apply transient w channel
			- sequence channels w specified slew rate


        DEPENDENCIES:
        pip install python-ivi (or xes variant) - xes driver ctrl
        pip install pyserial numpy  (pyvisa pyvisa-py pyusb)

"""

import ivi
import time
# find available instrument interfaces (ivi/pyvisa version?)
# import visa
# rm = visa.ResourceManager('@py')
# rm.list_resources()

 # connect:
n6 = ivi.agilent.agilentN6700B('ASRL::COM11,9600::INSTR') # prologix gpib-usb adapter
# n6 = ivi.agilent.agilentN6700B('USB0::2391::2311::<serial_number>::0::INSTR')# usb cable
# n6 = ivi.agilent.agilentN6700B('TCPIP0::192.168.1.108::INSTR') #ethernet port


#test communicaation (switch to ivi functions)
print(n6.query("*IDN?"))
n6.utility.reset_with_defaults()

# set display to all channels
n6.set_display_mode('all')

# configure and turn on channe 1
n6.outputs[0].voltage_level = 12.0
n6.outputs[0].current_limit = 1.0
n6.outputs[0].ovp_limit = 14.0
n6.outputs[0].ovp_enabled = True

# configure chan 2
n6.outputs[1].voltage_level = 28.0
n6.outputs[1].current_limit = 2.0
n6.outputs[1].ovp_limit = 50.0
n6.outputs[1].ovp_enabled = True

#turn on outputs
n6.outputs[0].enabled = True
n6.outputs[1].enabled = True
time.sleep(10)
n6.outputs[0].enabled = False
n6.outputs[1].enabled = False
# note, according the the n6700 manual, the fastest way to turn off/on outputs
# is to set the voltage to 0 / +vout vs enabling and disabling the channel
# enabling/disabling adds ~20ms to the turn on time.
# but if all channels are enabled at same time / coupled,
# all channels will turn on at same time + programmed delay.



# detect/force usage of sense lines or direct voltage sense

# how to measure voltage/current/power
print("voltage1: {.2F}".format())


# add names to channels
# is this possible? name attribute is locked


# how to turn on all channels at once with delay and slew
# test
# 33v, 20ms delay, 2v/ms ,ch1
# 5v   5ms delay, 8v/ms  , ch2
# 12v  0ms delay, 1v/ms  , ch3

rail = {"33v":0,
        "5v":1,
        "12v":2}

# 3.3v ch1
n6.outputs[rail["33v"]].ovp_limit =     4.3    # volts
n6.outputs[rail["33v"]].voltage_level = 3.30   # volts
n6.outputs[rail["33v"]].current_limit = 2.5    # amps
n6.outputs[rail["33v"]].slew_rate =     2.0    # v/ms
n6.outputs[rail["33v"]].turnon_delay = 20.0E-3 # seconds
n6.outputs[rail["33v"]].turnoff_delay = 0.01   # seconds

# 5v ch2
n6.outputs[rail["5v"]].ovp_limit = 6.0
n6.outputs[rail["5v"]].voltage_level = 5.0
n6.outputs[rail["5v"]].current_limit = 2.0
n6.outputs[rail["5v"]].slew_rate =     8.0
n6.outputs[rail["5v"]].turnon_delay =  5.0E-3
n6.outputs[rail["5v"]].turnoff_delay = 0.02

# 12v ch3
n6.outputs[rail["12v"]].ovp_limit = 14.0
n6.outputs[rail["12v"]].voltage_level = 12.0
n6.outputs[rail["12v"]].current_limit = 1.0
n6.outputs[rail["12v"]].slew_rate =     1.0
n6.outputs[rail["12v"]].turnon_delay =  0.0
n6.outputs[rail["12v"]].turnoff_delay = 0.0

# couple output state of channels 1,2,and 3
n6.set_channel_coupling(True, [0,1,2])
# n6700 rembers channel coupling after power cycle and reset

# turn on channels 1,2,3 simultaneously, works as replacement for coupling channels
n6.set_outputs_enabled(True, [0,1,2])
# n6._ask("*OPC?") # wait for channels to settle?
time.sleep(20)

#turn off channels
n6.set_outputs_enabled(False, [0,1,2])

# decouple channels
n6.set_channel_coupling(False)

# set display to just channel 4
n6.set_display_mode('single', chan = 3)


#reset and disconnect
n6.utility.reset()
n6.close()







# transient yet to be fixed
#
# transient = {}
# # upload transient
# # in uploader, verify thaat channel has high speed test option
# # "syst:chan:opt? (@4)"
# # assert 'Opt 054' in outputs[x].get_module_HW_options,
# #   "channel x does not have high speed test option for arbitrary waveform"
# # n6._write_chan("SOUR:VOLT:MODE LIST", 3)
# # n6.outputs[3].trigger_source = 'bus'
# # n6._write_chan('LIST:volt 1,2,3,4,5,6,7,8,9,10',3)
# # n6._write_chan('LIST:DWEL 1,2,0.5,1,0.25,1.5,0.1,1,0.75,1.2',3)
# #n6.
#
# #check [SOURce:]LIST:STEP, what to do after transient?
#
# # run transient
# #n6.
# # n6.outputs[3].enabled = True
# # n6._write("INIT:TRAN (@4)")
# # n6.send_software_trigger()
#
# # wait for completion
# n6._wait_busy()

