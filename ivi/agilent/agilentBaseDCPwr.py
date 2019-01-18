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
from .. import extra
from .. import scpi
from ..scpi import dcpwr as scpi_dcpwr

TrackingType = set(['floating'])
TriggerSourceMapping = {
        'immediate': 'IMM',
        'bus': 'BUS'}


class agilentBaseDCPwr(scpi.dcpwr.Base,
                       scpi.dcpwr.Trigger,
                       scpi.dcpwr.SoftwareTrigger,
                       scpi.dcpwr.Measurement):
    """"Generic SCPI IVI DC power supply driver"""

    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', '')

        # early define of _do_scpi_init
        self.__dict__.setdefault('_do_scpi_init', True)

        super(agilentBaseDCPwr, self).__init__(*args, **kwargs)

        self._self_test_delay = 5

        self._output_count = 1

        self._output_spec = [
            {
                'range': {
                    'P8V': (9.0, 20.0),
                    'P20V': (21.0, 10.0)
                },
                'ovp_max': 22.0,
                'voltage_max': 9.0,
                'current_max': 20.0
            }
        ]

        self._identity_description = "Generic SCPI DC power supply driver"
        self._identity_identifier = ""
        self._identity_revision = ""
        self._identity_vendor = ""
        self._identity_instrument_manufacturer = ""
        self._identity_instrument_model = ""
        self._identity_instrument_firmware_revision = ""
        self._identity_specification_major_version = 3
        self._identity_specification_minor_version = 0
        self._identity_supported_instrument_models = ['PSU']

        #self._init_outputs()

# copied in and made minor adjustments (mostly shortened commands, n6700 does not support full length commmands.)
# not tested
class Trigger(dcpwr.Trigger):
    # needs fixing. case of value and map dont match
    def _get_output_trigger_source(self, index):
        # trigger source for transient
        index = ivi.get_index(self._output_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = self._ask_chan("TRIG:TRAN:SOUR?", index).lower()
            print("got: "+ value)
            self._output_trigger_source[index] = [k for k, v in TriggerSourceMapping.items() if v == value][0]
        return self._output_trigger_source[index]

    # works
    def _set_output_trigger_source(self, index, value):
        index = ivi.get_index(self._output_name, index)
        value = str(value)
        if value not in TriggerSourceMapping:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            self._write_chan("TRIG:TRAN:SOUR %s" % TriggerSourceMapping[value], index)
        self._output_trigger_source[index] = value
        self._set_cache_valid(index=index)

    def _get_output_triggered_current_limit(self, index):
        index = ivi.get_index(self._output_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._output_triggered_current_limit[index] = float(
                self._ask_chan("SOUR:CURR:LEV:TRIG?", index))
            self._set_cache_valid(index=index)
        return self._output_triggered_current_limit[index]

    def _set_output_triggered_current_limit(self, index, value):
        index = ivi.get_index(self._output_name, index)
        value = float(value)
        if value < 0 or value > self._output_spec[index]['current_max']:
            raise ivi.OutOfRangeException()
        if not self._driver_operation_simulate:
            self._write_chan("SOUR:CURR:LEV:TRIG %.6f" % value, index)
        self._output_triggered_current_limit[index] = value
        self._set_cache_valid(index=index)

    def _get_output_triggered_voltage_level(self, index):
        index = ivi.get_index(self._output_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._output_triggered_voltage_level[index] = float(
                self._ask_chan("SOUR:VOLT:LEV:TRIG?", index))
            self._set_cache_valid(index=index)
        return self._output_triggered_voltage_level[index]

    def _set_output_triggered_voltage_level(self, index, value):
        index = ivi.get_index(self._output_name, index)
        value = float(value)
        if self._output_spec[index]['voltage_max'] >= 0:
            if value < 0 or value > self._output_spec[index]['voltage_max']:
                raise ivi.OutOfRangeException()
        else:
            if value > 0 or value < self._output_spec[index]['voltage_max']:
                raise ivi.OutOfRangeException()
        if not self._driver_operation_simulate:
            self._write_chan("SOUR:VOLT:LEV:TRIG %.6f" % value, index)
        self._output_triggered_voltage_level[index] = value
        self._set_cache_valid(index=index)

    # def _get_output_trigger_delay(self, index):
    #     index = ivi.get_index(self._output_name, index)
    #     if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
    #         self._output_trigger_delay[index] = float(
    #             self._ask_chan("trigger:delay?", index))
    #         self._set_cache_valid(index=index)
    #     return self._output_trigger_delay[index]
    #
    # def _set_output_trigger_delay(self, index, value):
    #     index = ivi.get_index(self._output_name, index)
    #     value = float(value)
    #     if value < 0:
    #         raise ivi.OutOfRangeException()
    #     if not self._driver_operation_simulate:
    #         self._write_chan("trigger:delay %.6f" % value, index)
    #     self._output_trigger_delay[index] = value
    #     self._set_cache_valid(index=index)

    def _trigger_abort(self):
        self._write('ABOR:TRAN')

    # broke
    def _trigger_initiate(self):
        if not self._driver_operation_simulate:
            self._write("INIT:TRAN, (1:4)")#initiate
            # add a single channel version.
            # replace 4 with actual number of channels


# copied in and made minor adjustments (mostly shortened commands, n6700b does not support full length commmands.)
# not sure if works
class OCP(extra.dcpwr.OCP):
    def _get_output_ocp_enabled(self, index):
        index = ivi.get_index(self._output_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._output_ocp_enabled[index] = bool(int(
                self._ask_chan("SOUR:CURR:PROT:STAT?", index)))
            self._set_cache_valid(index=index)
        return self._output_ocp_enabled[index]

    def _set_output_ocp_enabled(self, index, value):
        index = ivi.get_index(self._output_name, index)
        value = bool(value)
        if not self._driver_operation_simulate:
            self._write_chan("SOUR:CURR:PROT:STAT %s" % int(value), index)
        self._output_ocp_enabled[index] = value
        self._set_cache_valid(index=index)

    # N6700 doesnt support this? or it is programmed current limit/module current limit
    # def _get_output_ocp_limit(self, index):
    #     index = ivi.get_index(self._output_name, index)
    #     if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
    #         self._output_ocp_limit[index] = float(self._ask_chan("SOUR:CURR:PROT:LEV?", index))
    #         self._set_cache_valid(index=index)
    #     return self._output_ocp_limit[index]
    #
    # def _set_output_ocp_limit(self, index, value):
    #     index = ivi.get_index(self._output_name, index)
    #     value = float(value)
    #     if value < 0 or value > self._output_spec[index]['ocp_max']:
    #         raise ivi.OutOfRangeException()
    #     if not self._driver_operation_simulate:
    #         self._write_chan("SOUR:CURR:PROT:LEV %.1f" % value, index)
    #     self._output_ocp_limit[index] = value
    #     self._set_cache_valid(index=index)

    def _output_reset_output_protection(self, index):
        if not self._driver_operation_simulate:
            self._write_chan("OUTP:PROT:CLE", index)
            # self._write_chan("OUTP:PROT:CLE", index) # why duplicated in orig dcpwr?