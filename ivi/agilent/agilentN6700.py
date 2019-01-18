"""

Python Interchangeable Virtual Instrument Library

Copyright (c) 2013-2017 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""



from .. import ivi
from .. import dcpwr
from . import agilentBaseDCPwr
from .. import scpi

TrackingType = set(['floating'])
TriggerSourceMapping = {
        'bus': 'BUS',
        'external': 'EXT',
        'immediate': 'IMM',
        'TTL0': 'PIN1',
        'TTL1': 'PIN2',
        'TTL2': 'PIN3',
        'TTL3': 'PIN4',
        'TTL4': 'PIN5',
        'TTL5': 'PIN6',
        'TTL6': 'PIN7',
        'TTL7': 'PIN8',
        'transient_chan1': 'TRAN1', # channels are 1 inxexed here, but 0 indexed as index
        'transient_chan2': 'TRAN2',
        'transient_chan3': 'TRAN3',
        'transient_chan4': 'TRAN4',
        }


class agilentN6700(scpi.dcpwr.Base,
                   agilentBaseDCPwr.Trigger,
                   agilentBaseDCPwr.OCP,
                   scpi.dcpwr.SoftwareTrigger,
                   ):

    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', '')

        super(agilentN6700, self).__init__(*args, **kwargs)

        self._output_count = 0
        #self._output_count = self._get_output_module_number()

        self._output_spec = []
        #self._output_spec = self._get_output_module_specs()

        self._identity_description = "Agilent N6700 series IVI DC power supply driver"
        self._identity_identifier = ""
        self._identity_revision = ""
        self._identity_vendor = ""
        self._identity_instrument_manufacturer = "Agilent"
        self._identity_instrument_model = ""
        self._identity_instrument_firmware_revision = ""
        self._identity_specification_major_version = 0
        self._identity_specification_minor_version = 0
        self._identity_supported_instrument_models = ['N6700B', 'N6701B', 'N6702B',
                                                      'N6700C', 'N6701C', 'N6702C']

        self._add_property('outputs[].slew_rate',
                           self._get_output_slew_rate,
                           self._set_output_slew_rate)

        self._add_property('outputs[].turnon_delay',
                           self._get_output_ton_delay,
                           self._set_output_ton_delay)

        self._add_property('outputs[].turnoff_delay',
                           self._get_output_toff_delay,
                           self._set_output_toff_delay)

        self._init_outputs()


    def _init_outputs(self):
        try:
            super(agilentN6700, self)._init_outputs()
        except AttributeError:
            pass

        self._output_name = list()
        self._output_current_limit = list()
        self._output_current_limit_behavior = list()
        self._output_enabled = list()
        self._output_ovp_enabled = list()
        self._output_ovp_limit = list()
        self._output_voltage_level = list()
        self._output_voltage_max = list()
        self._output_slew_rate = list()
        self._output_turnOn_delay = list()
        self._output_turnOff_delay = list()
        for i in range(self._output_count):
            self._output_name.append("output%d" % (i+1))
            self._output_current_limit.append(self._output_spec[i-1]['current_max'])
            self._output_current_limit.append(0)
            self._output_current_limit_behavior.append('regulate')
            self._output_enabled.append(False)
            self._output_ovp_enabled.append(True)
            self._output_ovp_limit.append(self._output_spec[i-1]['ovp_max'])
            self._output_voltage_level.append(0)
            self._output_voltage_max.append(self._output_spec[i-1]['voltage_max'])
            self._output_slew_rate.append(0)
            self._output_turnOn_delay.append(0)
            self._output_turnOff_delay.append(0)

        self.outputs._set_list(self._output_name)

    # utilities
    # write command to specific channel
    def _write_chan(self, msg, channel):
        channel = channel + 1 # convert 0 indexed to 1 indexed
        return self._write(msg + ", (@{chan!s:s})".format(chan=channel))

    def _ask_chan(self, msg, channel):
        channel = channel + 1  # convert 0 indexed to 1 indexed
        return self._ask(msg + " (@{chan!s:s})".format(chan=channel))

    # Tested on agilent N6700B with N6752A modules; working
    def _get_output_current_limit(self, index):
        """
        This function fetches the output current limit setting of the instrument.
        """
        index = ivi.get_index(self._output_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._output_current_limit[index] = float(self._ask_chan("SOUR:CURR?", index))
            self._set_cache_valid(index=index)
        return self._output_current_limit[index]

    # Tested on agilent N6700B with N6752A modules; working
    def _set_output_current_limit(self, index, value):
        """
        This function sets the output current limit of the instrument.
        """
        index = ivi.get_index(self._output_name, index)
        value = float(value)
        if value < 0 or value > self._output_spec[index]['current_max']:
            raise ivi.OutOfRangeException()
        if not self._driver_operation_simulate:
            self._write_chan("SOUR:CURR %.2f" % float(value), index)
        self._output_current_limit[index] = value
        self._set_cache_valid(index=index)

    def _get_output_current_limit_behavior(self, index):
        index = ivi.get_index(self._output_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            value = int(self._ask_chan("SOUR:CURR:PROT:STAT?", index))
            if value:
                self._output_current_limit_behavior[index] = 'trip'
            else:
                self._output_current_limit_behavior[index] = 'regulate'
            self._set_cache_valid(index=index)
        return self._output_current_limit_behavior[index]

    def _set_output_current_limit_behavior(self, index, value):
        index = ivi.get_index(self._output_name, index)
        if value not in dcpwr.CurrentLimitBehavior:
            raise ivi.ValueNotSupportedException()
        value = bool(value == 'trip')
        if not self._driver_operation_simulate:
            self._write_chan("SOUR:CURR:PROT:STAT %.2f" % value, index)
        self._output_current_limit_behavior[index] = value
        for k in range(self._output_count):
            self._set_cache_valid(valid=False, index=k)
        self._set_cache_valid(index=index)

    # Tested on agilent N6700B with N6752A modules; working
    def _get_output_enabled(self, index):
        """
        This function queries the output state of the instrument.
        """
        index = ivi.get_index(self._output_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            result = int(self._ask_chan(":OUTP?", index))

            self._set_cache_valid(index=index)
        return self._output_enabled[index]

    # Tested on agilent N6700B with N6752A modules; working
    def _set_output_enabled(self, index, value):
        """
        This function sets the output state of the instrument.
        """
        index = ivi.get_index(self._output_name, index)
        value = int(value)#convert true/false to 1/0
        if not self._driver_operation_simulate:
            self._write_chan(":OUTP %s" % str(value), index)
        self._output_enabled[index] = value
        for k in range(self._output_count):
            self._set_cache_valid(valid=False, index=k)
        self._set_cache_valid(index=index)

    # Tested on agilent N6700B with N6752A modules; working
    def _get_output_voltage_level(self, index):
        """
        This function fetches the output voltage setting of the instrument.
        """
        index = ivi.get_index(self._output_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._output_voltage_level[index] = float(self._ask_chan("SOUR:VOLT?", index))
            self._set_cache_valid(index=index)
        return self._output_voltage_level[index]

    # Tested on agilent N6700B with N6752A modules; working
    def _set_output_voltage_level(self, index, value):
        """
        This function sets the output voltage of the instrument.
        """
        index = ivi.get_index(self._output_name, index)
        value = float(value)
        if value < 0 or value > self._output_voltage_max[index]:
            raise ivi.OutOfRangeException()
        if not self._driver_operation_simulate:
            self._write_chan("SOUR:VOLT %.2f" % float((value)), index)
        self._output_voltage_level[index] = value
        self._set_cache_valid(index=index)

    # Tested on agilent N6700B with N6752A modules; working
    def _get_output_ovp_limit(self, index):
        """
        This function fetches the OVP limit.
        """
        index = ivi.get_index(self._output_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._output_ovp_limit[index] = float(self._ask_chan("SOUR:VOLT:PROT:LEV?", index))
            self._set_cache_valid(index=index)
        return self._output_ovp_limit[index]

    # Tested on agilent N6700B with N6752A modules; working
    def _set_output_ovp_limit(self, index, value):
        """
        This function sets the OVP limit.
        """
        index = ivi.get_index(self._output_name, index)
        value = float(value)
        if value < 0 or value > self._output_spec[index]['ovp_max']:
            raise ivi.OutOfRangeException()
        if not self._driver_operation_simulate:
            self._write_chan("SOUR:VOLT:PROT:LEV %.1f" % value, index)
        self._output_ovp_limit[index] = value
        self._set_cache_valid(index=index)

    # Tested on agilent N6700B with N6752A modules; working
    def _output_measure(self, index, type):
        """
        This function measures the voltage or current of the output.
        """
        index = ivi.get_index(self._output_name, index)

        # does this comply with what ivi expects for mapping?
        outputMeasurementMap = {'voltage': 'VOLT',
                    'voltage_rms': 'VOLT:ACDC',
                    'voltage_high': 'VOLT:HIGH',
                    'voltage_low': 'VOLT:LOW',
                    'voltage_max': 'VOLT:MAX',
                    'voltage_min': 'VOLT:MIN',
                    'current': 'CURR',
                    'current_rms': 'CURR:ACDC',
                    'current_high': 'CURR:HIGH',
                    'current_low': 'CURR:LOW',
                    'current_max': 'CURR:MAX',
                    'current_min': 'CURR:MIN',
                    'power': 'POW'}

        if type not in outputMeasurementMap:
            raise ivi.ValueNotSupportedException()
        else:
            if not self._driver_operation_simulate:
                return float(self._ask_chan("MEAS:{}?".format(
                                outputMeasurementMap[type]), index))
        return 0

    # Tested on agilent N6700B with N6752A modules; working
    def _get_output_slew_rate(self, index):
        """
        This function queries the output voltage slew rate.
        Values returned are in V/ms
        """
        index = ivi.get_index(self._output_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._output_slew_rate[index] = float(self._ask_chan("SOUR:VOLT:SLEW?", index))
            self._set_cache_valid(index=index)
        return self._output_slew_rate[index]

    # Tested on agilent N6700B with N6752A modules; working
    def _set_output_slew_rate(self, index, value):
        """
        This function sets the output voltage slew rate. Ranges for the 6700 series are:
        * N6752A: 0.0000476V/ms,MIN - 9.9E+35V/ms,max ?
        """
        index = ivi.get_index(self._output_name, index)

        delayValues = {'min': "MIN",
                       'max': 'MAX',
                       'infinite': 'INF'}
        if isinstance(value, str) and value.lower() in delayValues:
            value = delayValues[value.lower()]
        else:
            # limits for channel delay
            if 0.0 >= value:
                value = 'MIN'
                raise ivi.OutOfRangeException()
            elif value >= 9.90E+35:
                value = 'MAX'
            else:
                value = ("%.2e" % float(value * 1000)) # convert v/s to v/ms

        if not self._driver_operation_simulate:
            self._write_chan("SOUR:VOLT:SLEW %.3f" % float(value), index)
        self._output_slew_rate[index] = value
        for k in range(self._output_count):
            self._set_cache_valid(valid=False, index=k)
        self._set_cache_valid(index=index)


    def _get_output_ton_delay(self, index):
        index = ivi.get_index(self._output_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._output_turnOn_delay[index] = float((self._ask_chan("OUTP:DEL:RISE?", index))) #output:delay:rise
            self._set_cache_valid(index=index)
        return self._output_turnOn_delay[index]

    def _set_output_ton_delay(self, index, value):
        """
        This function sets the amount of time a
        channel is delayed from turning on in seconds
        """
        index = ivi.get_index(self._output_name, index)
        delayValues = {'min': 'MIN',
                       'max': 'MAX'}
        if isinstance(value, str) and value.lower() in delayValues:
            value = delayValues[value.lower()]
        else:
            # limits for channel delay
            if 1.03E-4 >= value:
                value = 'MIN'
            elif value >= 1.023E+3:
                value = 'MAX'
            else:
                value = ("%.2e" % float(value))
        if not self._driver_operation_simulate:
            self._write_chan("OUTP:DEL:RISE {value}".format( value=value), index)
        self._output_turnOn_delay[index] = value
        for k in range(self._output_count):
            self._set_cache_valid(valid=False, index=k)
        self._set_cache_valid(index=index)


    def _get_output_ton_delay(self, index):
        index = ivi.get_index(self._output_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._output_turnOff_delay[index] = float((self._ask_chan("OUTP:DEL:FALL?", index))) #output:delay:fall
            self._set_cache_valid(index=index)
        return self._output_turnOff_delay[index]

    def _set_output_toff_delay(self, index, value):
        """
        This function sets the amount of time a
        channel is delayed from turning off in seconds
        """
        index = ivi.get_index(self._output_name, index)
        delayValues = {'min': 'MIN',
                       'max': 'MAX'}
        if isinstance(value, str) and value.lower() in delayValues:
            value = delayValues[value.lower()]
        else:
            # limits for channel delay
            if 1.03E-4 >= value:
                value = 'MIN'
            elif value >= 1.023E+3:
                value = 'MAX'
            else:
                value = ("%.2e" % float(value))  # instrument expects exponential notation

        if not self._driver_operation_simulate:
            self._write_chan("OUTP:DEL:FALL {value}".format( value=value), index)
        self._output_turnOff_delay[index] = value
        for k in range(self._output_count):
            self._set_cache_valid(valid=False, index=k)
        self._set_cache_valid(index=index)

    def _get_output_module_number(self):
        return int(self._ask("SYST:CHAN?")[1:])

    def _get_output_module_specs(self):
        # automatic spec populator
        # move this to its own file for series?
        module_list = {
            "N6752A":
                {
                    'range': {  # N6752A module
                        'P50V': (50.0, 10.0)
                    },
                    'ovp_max': 55.0,
                    'ocp_max': 10.2,
                    'voltage_max': 51.0,
                    'current_max': 10.2
                },
            # default:
            #     {
            #         'range': {  # unknown module
            #             'P50V': (0.0, 0.0)
            #         },  # can maybe get these values from the default settings of the modules
            #         'ovp_max': 0.0, self._get_output_ovp_limit(chan) # currently set ovp/ocp should serve as good standins.
            #         'ocp_max': 0.0, self._get_output_ocp_limit(chan)
            #         'voltage_max': 0.0, #SOUR:VOLT:RANG? (@2)
            #         'current_max': 0.0  #SOUR:CURR:RANG? (@2)
            #     },
        }
        output_specs = []
        for moduleNum in range(0, self._output_count):
            module_model = str(self._ask_chan("syst:chan:mod?", moduleNum))
            output_specs.insert(moduleNum, module_list[module_model])
        return output_specs

    def get_module_HW_options(self, index):
        """
        this function gats a list of installed options per channel.
        example = ['052', 'j01']
        was only tested on channels with a single option.
        """
        index = ivi.get_index(self._output_name, index)
        option_list = self._ask_chan("SYST:CHAN:OPT?", index).split(',')
        option_list = [opt.replace('"', '') for opt in options]
        return option_list

    def set_display_mode(self, view, chan=0):
        """
        this function sets the display view for all channels or a single channel
        """
        index = ivi.get_index(self._output_name, chan)
        if view not in ['all', 'single']:
            raise ivi.ValueNotSupportedException()
        if view == 'all':
            self._write("DISP:VIEW METER4")  # 4 channel meter display
        if view == 'single':
            # instead of "single", just send channel numbe to display in view?
            channel = index + 1  # 0 index to 1 index
            self._write("DISP:VIEW METER1")  # single channel meter display
            self._write("DISP:CHAN {}".format(channel))  # select channel for single meter view

    # Tested on agilent N6700B with N6752A modules; working
    def set_channel_coupling(self, value, indexes=[]):
        indexes = [ivi.get_index(self._output_name, index) for index in indexes]

        if value is False:
            self._write('OUTP:COUP 0')
        else:
            self._write('OUTP:COUP 1')
            self._write('OUTP:COUP:CHAN {}'.format(','.join(str(v+1) for v in indexes)))

    # Tested on agilent N6700B with N6752A modules; working
    def set_outputs_enabled(self, value, indexes):
        """
        This function sets the output state of the
        instrument on multiple channels simultaneously
        value = True/False
        indexes = [0,1,2,3]
        """
        indexes = [ivi.get_index(self._output_name, index) for index in indexes]

        if not self._driver_operation_simulate:
            self._write(":OUTP {!s}, (@{})"
                        .format(int(value), ','.join(str(v+1) for v in indexes)))
        for index in indexes:
            self._output_enabled[index] = value
        for k in range(self._output_count):
            self._set_cache_valid(valid=False, index=k)

    # extra, non ivi functions:
    def get_ttl(self):
        return int(self._ask('SOUR:DIG:INP:DATA?'))

    def set_ttl(self, value):
        if (0 >= int(value) <= 255):
            raise AssertionError('Value out of range. 0 - 255')
        self._write('SOUR:DIG:OUTP:DATA ' + str(value))

    def set_ttl_function(self, pin, function, polarity="POSITIVE"):
        pin_functions = ['DIO', 'DINPUT',
                         'TOUTPUT', 'TINPUT',
                         'FAULT', 'INHIBIT',
                         'ONCOUPLE', 'OFFCOUPLE']
        assert 0 >= pin <= 7, "invalid pin number {}".format(pin)
        assert function.upper() in pin_functions, 'Invalid pin function: {}'.format(function)
        assert polarity in ['POSitive', 'NEGative'], 'invalid pin polarity {}'.format(polarity)
        self.write('source:digital:pin{}:function {}'.format(pin, function))
        self.write('source:digital:pin{}:polarity {}'.format(pin, polarity))

   # # load / run fast arbitrary voltage sequences on power supply
    # def load_sequence(self, index, sequence):
    #     index = ivi.get_index(self._output_name, index)
    #     assert sequence.__len__() <= 200, "maximum number of points exceeded"
    #
    # assert 'Opt 054' in outputs[x].get_module_HW_options,
    # #   "channel x does not have high speed test option for arbitrary waveform"
    #   sequence_values = ["VOLT", "CURRENT", "dwell]
    #
    #     # cant set slew independantly for each voltage step unfortionately
    #     sequence = {
    #                 "volt":[1,2,3,4,5,6,7,8,9,10],
    #                 "CURR": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    #                 "dwell":[1,2,0.5,1,0.25,1.5,0.1,1,0.75,1.2]
    #     }
    #     list = [1,2,3,4,5]
    #     cmd = "LIST:VOLT {}".format(','.join(str(v) for v in list))
    #
    # copied over not fixed
    # self._write_chan("SOUR:VOLT:MODE LIST", 3)
    # self.outputs[3].trigger_source = 'bus'
    #
    # self._write('list:volt {lst}, {}'.format(lst=','.join(str(v) for v in sequence[],)
    # self._write_chan('LIST:volt 1,2,3,4,5,6,7,8,9,10', 3)
    # self._write_chan('LIST:DWEL 1,2,0.5,1,0.25,1.5,0.1,1,0.75,1.2', 3)
    #
    # # enable output
    # self.outputs[3].enabled = 1
    #
    # # trigger transient
    # self._write("INIT:TRAN (@4)")
    # self.send_software_trigger()
    #
    # def run_sequence(self):
    #     # enable output
    #     # self.outputs[].enabled = 1
    #     #
    #     # # trigger transient
    #     # self._write("INIT:TRAN (@4)")
    #     # self.send_software_trigger()

# # probably works
#     # load / run fast arbitrary voltage sequences on power supply
#     def load_sequence(self, index, sequence):
#         index = ivi.get_index(self._output_name, index)
#         assert 'Opt 054' in outputs[x].get_module_HW_options, \
#             "module {} does not have high speed test option".format(self.id)
#
#
#         seq_values = ["volt", "current", "dwell", "toutput:bostep", "toutput:eostep", ]
#         # cant set slew independantly for each voltage step unfortionately
#         # sequence = {
#         #             "volt": [1,2,3,4,5,6,7,8,9,10],
#         #             "currrent": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
#         #             "dwell": [1,2,0.5,1,0.25,1.5,0.1,1,0.75,1.2]
#         # }
#
#         # sanity check
#         numsteps = len(sequence["dwell"])
#         assert numsteps <= 512, "maximum number of steps exceeded"
#         for list in sequence:
#             assert list in seq_values, "{} is not a valid function: {}"\
#                 .format(list,", ".join(seq_values))
#             assert len(list) == numsteps, \
#                 "function {} in sequence does not have correct number of steps"\
#                     .format(list)
#
#         for list in sequence:
#             if list is not "dwell":
#                 self.write("SOUR:{fcn}:MODE LIST, {id}".format(fcn=list, id=self.id))
#             self.write('list:{fcn} {lst}, {id}'.format(
#                             fcn= list,
#                             lst=','.join([str(v) for v in list],
#                             id='(@{})')))
#
#             num_points = self.query('source:list:{fcn}:points?'.format())
#             assert num_points == len(sequence[list])
#
#         self.trigger_source = 'bus'
#
#     def run_sequence(self):
#         # enable output
#         self.enabled = 1
#
#         # trigger transient
#         self.write("INIT:TRAN {}".format(id=self.id))
#         self.send_software_trigger()


