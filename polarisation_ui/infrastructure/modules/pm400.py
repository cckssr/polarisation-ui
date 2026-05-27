#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import (
    strict_discrete_set,
    truncated_range,
)


class ThorlabsPM400(SCPIMixin, Instrument):
    """Represents the Thorlabs PM400 Optical Power and Energy Meter.

    Commands are compatible with PM100A, PM100D, PM100USB, and PM160 consoles.

    :param adapter: A string (VISA resource name) or Adapter subclass object.
    :param name: The name of the instrument.
    :param kwargs: Additional keyword arguments passed to the Instrument.

    Example usage::

        pm = ThorlabsPM400("USB0::0x1313::0x8078::P0000001::INSTR")
        print(pm.power)
        pm.wavelength = 1550
        pm.configure = "POW"
    """

    def __init__(self, adapter, name="Thorlabs PM400", **kwargs):
        super().__init__(adapter, name, **kwargs)

    self_test = Instrument.measurement(
        "*TST?",
        """Measure the self-test result (bool, True=passed, False=failed).""",
        values={True: 0, False: 1},
        map_values=True,
    )

    beeper_state = Instrument.control(
        "SYST:BEEP:STAT?",
        "SYST:BEEP:STAT %d",
        """Control the beeper enabled state (bool).""",
        values={True: 1, False: 0},
        map_values=True,
    )

    error = Instrument.measurement(
        "SYST:ERR?",
        """Get the latest error code and message from the error queue (list).""",
    )

    scpi_version = Instrument.measurement(
        "SYST:VERS?",
        """Get the SCPI standard version level (float).""",
        cast=float,
    )

    date = Instrument.control(
        "SYST:DATE?",
        "SYST:DATE %s",
        """Control the instrument calendar date; getter returns [year, month, day] as floats, setter takes 'year,month,day' string.""",
    )

    time = Instrument.control(
        "SYST:TIME?",
        "SYST:TIME %s",
        """Control the instrument clock time; getter returns [hour, min, sec] as floats, setter takes 'hour,min,sec' string.""",
    )

    line_frequency = Instrument.control(
        "SYST:LFREQ?",
        "SYST:LFREQ %g",
        """Control the AC line frequency in Hz (float, strictly from 50 or 60).""",
        validator=strict_discrete_set,
        values=[50, 60],
        cast=float,
    )

    sensor_info = Instrument.measurement(
        "SYST:SENS:IDN?",
        """Get the sensor identification fields: name, serial, cal_msg, type, subtype, flags (list).""",
    )

    status_measurement_event = Instrument.measurement(
        "STAT:MEAS:EVEN?",
        """Get the measurement event register value (int).""",
        cast=int,
    )

    status_measurement_condition = Instrument.measurement(
        "STAT:MEAS:COND?",
        """Get the measurement condition register value (int).""",
        cast=int,
    )

    status_measurement_positive_transition = Instrument.control(
        "STAT:MEAS:PTR?",
        "STAT:MEAS:PTR %d",
        """Control the measurement positive transition filter register (int).""",
        cast=int,
    )

    status_measurement_negative_transition = Instrument.control(
        "STAT:MEAS:NTR?",
        "STAT:MEAS:NTR %d",
        """Control the measurement negative transition filter register (int).""",
        cast=int,
    )

    status_measurement_enable = Instrument.control(
        "STAT:MEAS:ENAB?",
        "STAT:MEAS:ENAB %d",
        """Control the measurement event enable register (int).""",
        cast=int,
    )

    status_auxiliary_event = Instrument.measurement(
        "STAT:AUX:EVEN?",
        """Get the auxiliary event register value (int).""",
        cast=int,
    )

    status_auxiliary_condition = Instrument.measurement(
        "STAT:AUX:COND?",
        """Get the auxiliary condition register value (int).""",
        cast=int,
    )

    status_auxiliary_positive_transition = Instrument.control(
        "STAT:AUX:PTR?",
        "STAT:AUX:PTR %d",
        """Control the auxiliary positive transition filter register (int).""",
        cast=int,
    )

    status_auxiliary_negative_transition = Instrument.control(
        "STAT:AUX:NTR?",
        "STAT:AUX:NTR %d",
        """Control the auxiliary negative transition filter register (int).""",
        cast=int,
    )

    status_auxiliary_enable = Instrument.control(
        "STAT:AUX:ENAB?",
        "STAT:AUX:ENAB %d",
        """Control the auxiliary event enable register (int).""",
        cast=int,
    )

    status_operation_event = Instrument.measurement(
        "STAT:OPER:EVEN?",
        """Get the operation event register value (int).""",
        cast=int,
    )

    status_operation_condition = Instrument.measurement(
        "STAT:OPER:COND?",
        """Get the operation condition register value (int).""",
        cast=int,
    )

    status_operation_positive_transition = Instrument.control(
        "STAT:OPER:PTR?",
        "STAT:OPER:PTR %d",
        """Control the operation positive transition filter register (int).""",
        cast=int,
    )

    status_operation_negative_transition = Instrument.control(
        "STAT:OPER:NTR?",
        "STAT:OPER:NTR %d",
        """Control the operation negative transition filter register (int).""",
        cast=int,
    )

    status_operation_enable = Instrument.control(
        "STAT:OPER:ENAB?",
        "STAT:OPER:ENAB %d",
        """Control the operation event enable register (int).""",
        cast=int,
    )

    status_questionable_event = Instrument.measurement(
        "STAT:QUES:EVEN?",
        """Get the questionable event register value (int).""",
        cast=int,
    )

    status_questionable_condition = Instrument.measurement(
        "STAT:QUES:COND?",
        """Get the questionable condition register value (int).""",
        cast=int,
    )

    status_questionable_positive_transition = Instrument.control(
        "STAT:QUES:PTR?",
        "STAT:QUES:PTR %d",
        """Control the questionable positive transition filter register (int).""",
        cast=int,
    )

    status_questionable_negative_transition = Instrument.control(
        "STAT:QUES:NTR?",
        "STAT:QUES:NTR %d",
        """Control the questionable negative transition filter register (int).""",
        cast=int,
    )

    status_questionable_enable = Instrument.control(
        "STAT:QUES:ENAB?",
        "STAT:QUES:ENAB %d",
        """Control the questionable event enable register (int).""",
        cast=int,
    )

    display_brightness = Instrument.control(
        "DISP:BRIG?",
        "DISP:BRIG %g",
        """Control the display brightness as a fraction from 0.0 to 1.0 (float).""",
        cast=float,
    )

    display_contrast = Instrument.control(
        "DISP:CONT?",
        "DISP:CONT %g",
        """Control the display contrast as a fraction from 0.0 to 1.0 (float).""",
        cast=float,
    )

    calibration_string = Instrument.measurement(
        "CAL:STR?",
        """Get the human-readable sensor calibration message string (str).""",
    )

    averaging_count = Instrument.control(
        "SENS:AVER:COUN?",
        "SENS:AVER:COUN %d",
        """Control the number of samples to average per measurement (int, truncated from 1 to 300000).""",
        validator=truncated_range,
        values=[1, 300000],
        cast=int,
    )

    attenuation = Instrument.control(
        "SENS:CORR:LOSS:INP:MAGN?",
        "SENS:CORR:LOSS:INP:MAGN %g",
        """Control the user attenuation correction factor in dB (float, truncated from -60 to 90).""",
        validator=truncated_range,
        values=[-60, 90],
        cast=float,
    )

    zero_state = Instrument.measurement(
        "SENS:CORR:COLL:ZERO:STAT?",
        """Get the zero adjustment routine status code (int).""",
        cast=int,
    )

    zero_magnitude = Instrument.measurement(
        "SENS:CORR:COLL:ZERO:MAGN?",
        """Get the current stored zero offset value (float).""",
        cast=float,
    )

    beam_diameter = Instrument.control(
        "SENS:CORR:BEAM?",
        "SENS:CORR:BEAM %g",
        """Control the beam diameter in mm used for power/energy density calculations (float).""",
        cast=float,
    )

    wavelength = Instrument.control(
        "SENS:CORR:WAV?",
        "SENS:CORR:WAV %g",
        """Control the operating wavelength in nm for spectral correction (float).""",
        cast=float,
    )

    photodiode_response = Instrument.control(
        "SENS:CORR:POW:PDI:RESP?",
        "SENS:CORR:POW:PDI:RESP %g",
        """Control the photodiode sensor response in A/W (float).""",
        cast=float,
    )

    thermopile_response = Instrument.control(
        "SENS:CORR:POW:THER:RESP?",
        "SENS:CORR:POW:THER:RESP %g",
        """Control the thermopile sensor response in V/W (float).""",
        cast=float,
    )

    pyro_response = Instrument.control(
        "SENS:CORR:ENER:PYRO:RESP?",
        "SENS:CORR:ENER:PYRO:RESP %g",
        """Control the pyroelectric sensor response in V/J (float).""",
        cast=float,
    )

    current_autorange = Instrument.control(
        "SENS:CURR:RANG:AUTO?",
        "SENS:CURR:RANG:AUTO %d",
        """Control the current auto-ranging enabled state (bool).""",
        values={True: 1, False: 0},
        map_values=True,
    )

    current_range = Instrument.control(
        "SENS:CURR:RANG:UPP?",
        "SENS:CURR:RANG:UPP %g",
        """Control the upper current measurement range limit in A (float).""",
        cast=float,
    )

    current_reference = Instrument.control(
        "SENS:CURR:REF?",
        "SENS:CURR:REF %g",
        """Control the current delta mode reference value in A (float).""",
        cast=float,
    )

    current_delta_mode = Instrument.control(
        "SENS:CURR:STAT?",
        "SENS:CURR:STAT %d",
        """Control the current delta measurement mode enabled state (bool).""",
        values={True: 1, False: 0},
        map_values=True,
    )

    energy_range = Instrument.control(
        "SENS:ENER:RANG:UPP?",
        "SENS:ENER:RANG:UPP %g",
        """Control the upper energy measurement range limit in J (float).""",
        cast=float,
    )

    energy_reference = Instrument.control(
        "SENS:ENER:REF?",
        "SENS:ENER:REF %g",
        """Control the energy delta mode reference value in J (float).""",
        cast=float,
    )

    energy_delta_mode = Instrument.control(
        "SENS:ENER:STAT?",
        "SENS:ENER:STAT %d",
        """Control the energy delta measurement mode enabled state (bool).""",
        values={True: 1, False: 0},
        map_values=True,
    )

    frequency_range_upper = Instrument.measurement(
        "SENS:FREQ:RANG:UPP?",
        """Get the upper frequency measurement range limit in Hz (float).""",
        cast=float,
    )

    frequency_range_lower = Instrument.measurement(
        "SENS:FREQ:RANG:LOW?",
        """Get the lower frequency measurement range limit in Hz (float).""",
        cast=float,
    )

    power_autorange = Instrument.control(
        "SENS:POW:RANG:AUTO?",
        "SENS:POW:RANG:AUTO %d",
        """Control the power auto-ranging enabled state (bool).""",
        values={True: 1, False: 0},
        map_values=True,
    )

    power_range = Instrument.control(
        "SENS:POW:RANG:UPP?",
        "SENS:POW:RANG:UPP %g",
        """Control the upper power measurement range limit in W (float).""",
        cast=float,
    )

    power_reference = Instrument.control(
        "SENS:POW:REF?",
        "SENS:POW:REF %g",
        """Control the power delta mode reference value in W (float).""",
        cast=float,
    )

    power_delta_mode = Instrument.control(
        "SENS:POW:STAT?",
        "SENS:POW:STAT %d",
        """Control the power delta measurement mode enabled state (bool).""",
        values={True: 1, False: 0},
        map_values=True,
    )

    power_unit = Instrument.control(
        "SENS:POW:UNIT?",
        "SENS:POW:UNIT %s",
        """Control the power measurement unit (str, strictly 'W' or 'DBM').""",
        validator=strict_discrete_set,
        values=["W", "DBM"],
    )

    voltage_autorange = Instrument.control(
        "SENS:VOLT:RANG:AUTO?",
        "SENS:VOLT:RANG:AUTO %d",
        """Control the voltage auto-ranging enabled state (bool).""",
        values={True: 1, False: 0},
        map_values=True,
    )

    voltage_range = Instrument.control(
        "SENS:VOLT:RANG:UPP?",
        "SENS:VOLT:RANG:UPP %g",
        """Control the upper voltage measurement range limit in V (float).""",
        cast=float,
    )

    voltage_reference = Instrument.control(
        "SENS:VOLT:REF?",
        "SENS:VOLT:REF %g",
        """Control the voltage delta mode reference value in V (float).""",
        cast=float,
    )

    voltage_delta_mode = Instrument.control(
        "SENS:VOLT:STAT?",
        "SENS:VOLT:STAT %d",
        """Control the voltage delta measurement mode enabled state (bool).""",
        values={True: 1, False: 0},
        map_values=True,
    )

    peak_threshold = Instrument.control(
        "SENS:PEAK:THR?",
        "SENS:PEAK:THR %g",
        """Control the peak detector trigger level in % of full scale (float, truncated from 0 to 100).""",
        validator=truncated_range,
        values=[0, 100],
        cast=float,
    )

    photodiode_filter = Instrument.control(
        "INP:PDI:FILT:LPAS:STAT?",
        "INP:PDI:FILT:LPAS:STAT %d",
        """Control the photodiode low-pass bandwidth filter enabled state (bool, True=low BW).""",
        values={True: 1, False: 0},
        map_values=True,
    )

    thermopile_accelerator = Instrument.control(
        "INP:THER:ACC:STAT?",
        "INP:THER:ACC:STAT %d",
        """Control the thermopile response time accelerator enabled state (bool).""",
        values={True: 1, False: 0},
        map_values=True,
    )

    thermopile_accelerator_auto = Instrument.control(
        "INP:THER:ACC:AUTO?",
        "INP:THER:ACC:AUTO %d",
        """Control the thermopile accelerator automatic mode enabled state (bool).""",
        values={True: 1, False: 0},
        map_values=True,
    )

    thermopile_tau = Instrument.control(
        "INP:THER:ACC:TAU?",
        "INP:THER:ACC:TAU %g",
        """Control the thermopile 0–63% response time constant in s (float, truncated from 1 to 30).""",
        validator=truncated_range,
        values=[1, 30],
        cast=float,
    )

    adapter_type = Instrument.control(
        "INP:ADP:TYPE?",
        "INP:ADP:TYPE %s",
        """Control the default sensor adapter type (str, strictly 'PHOT', 'THER', or 'PYRO').""",
        validator=strict_discrete_set,
        values=["PHOT", "THER", "PYRO"],
    )

    configure = Instrument.control(
        "CONF?",
        "CONF:%s",
        """Control the active measurement configuration (str, strictly 'POW', 'CURR', 'VOLT', 'ENER', 'FREQ', 'PDEN', 'EDEN', 'RES', or 'TEMP').""",
        validator=strict_discrete_set,
        values=["POW", "CURR", "VOLT", "ENER", "FREQ", "PDEN", "EDEN", "RES", "TEMP"],
    )

    power = Instrument.measurement(
        "MEAS:POW?",
        """Measure the optical power in W (float).""",
        cast=float,
    )

    current = Instrument.measurement(
        "MEAS:CURR?",
        """Measure the detector current in A (float).""",
        cast=float,
    )

    voltage = Instrument.measurement(
        "MEAS:VOLT?",
        """Measure the detector voltage in V (float).""",
        cast=float,
    )

    energy = Instrument.measurement(
        "MEAS:ENER?",
        """Measure the pulse energy in J (float).""",
        cast=float,
    )

    frequency = Instrument.measurement(
        "MEAS:FREQ?",
        """Measure the pulse repetition frequency in Hz (float).""",
        cast=float,
    )

    power_density = Instrument.measurement(
        "MEAS:PDEN?",
        """Measure the power density in W/cm² (float).""",
        cast=float,
    )

    energy_density = Instrument.measurement(
        "MEAS:EDEN?",
        """Measure the energy density in J/cm² (float).""",
        cast=float,
    )

    resistance = Instrument.measurement(
        "MEAS:RES?",
        """Measure the sensor presence resistance in Ohm (float).""",
        cast=float,
    )

    temperature = Instrument.measurement(
        "MEAS:TEMP?",
        """Measure the sensor temperature in °C (float).""",
        cast=float,
    )

    fetch = Instrument.measurement(
        "FETC?",
        """Get the last measurement result without triggering a new acquisition (float).""",
        cast=float,
    )

    read_measurement = Instrument.measurement(
        "READ?",
        """Measure by triggering a new acquisition and returning the result (float).""",
        cast=float,
    )

    def beep(self):
        """Issue an immediate audible beep."""
        self.write("SYST:BEEP:IMM")

    def status_preset(self):
        """Return all status registers to their default power-on states."""
        self.write("STAT:PRES")

    def zero(self):
        """Start the zero adjustment routine."""
        self.write("SENS:CORR:COLL:ZERO:INIT")

    def abort_zero(self):
        """Abort the running zero adjustment routine."""
        self.write("SENS:CORR:COLL:ZERO:ABOR")

    def initiate(self):
        """Take the instrument out of idle state to start a measurement."""
        self.write("INIT")

    def abort(self):
        """Abort the current measurement and return to idle state."""
        self.write("ABOR")
