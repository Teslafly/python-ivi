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

from .agilentN6700 import *

class agilentN6700B(agilentN6700):
    "Agilent N6300B series IVI DC power supply driver"

    # max 400w total
    "note: when developing for the n6700 mainframe over usb, improper commands" \
        "will cause the mainframe to lock up until power cycled." \
        "The symptom of this is pipe errors when trying to send commands."
    
    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', 'N6700B')

        super(agilentN6700B, self).__init__(*args, **kwargs)

        # self._output_count = 4
        self._output_count = self._get_output_module_number()
        # move this to generic mainframe handler
        # move to function , and check chan # between 1 and 4
        #define min and max channels as variables
        # verify instrument model when loading

        self._output_spec = self._get_output_module_specs()

        # self._output_spec = [
        #     {
        #         'range': {  # N6752A module
        #             'P50V': (50.0, 10.0)
        #         },
        #         'ovp_max': 55.0,
        #         'ocp_max': 10.2,
        #         'voltage_max': 50.0,
        #         'current_max': 10.0
        #     },
        #     {
        #         'range': {  # N6752A module
        #             'P50V': (50.0, 10.0)
        #         },
        #         'ovp_max': 55.0,
        #         'ocp_max': 10.2,
        #         'voltage_max': 50.0,
        #         'current_max': 10.0
        #     },
        #     {
        #         'range': {  # N6752A module
        #             'P50V': (50.0, 10.0)
        #         },
        #         'ovp_max': 55.0,
        #         'ocp_max': 10.2,
        #         'voltage_max': 50.0,
        #         'current_max': 10.0
        #     },
        #     {
        #         'range': {  # N6752A module
        #             'P50V': (50.0, 10.0)
        #         },
        #         'ovp_max': 55.0,
        #         'ocp_max': 10.2,
        #         'voltage_max': 50.0,
        #         'current_max': 10.0
        #     },
        # ]
        
        self._init_outputs()



    
    
