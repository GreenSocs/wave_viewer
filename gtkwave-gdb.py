#
# Copyright (C) 2019 GreenSocs SAS.
#
# Author: Damien Hedde
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""
gtkwave-gdb.py:

This module adds gtkwave related commands to gdb ui.
It can be loaded in gd using the 'source gtkwave-gdb.py' command.

It adds 2 commands:
    + gtkwave-set-time ts      set current displayed time
    + gtkwave-toggle-dyn-time  toggle dynamic time display

Control socket used to send the commands can be changed with the
gtkwave-socket parameter. The socket is initialized with the
GTKWAVE_CONTROL_SOCKET environment variable.
"""

import gdb
import socket
import re
import os


def gtkwave_socket_param(s):
    mo = re.match("(.*):([0-9]+)$", s)
    if not mo:
        return None
    addr = mo.group(1)
    if not len(addr):
        addr = "localhost"
    return (addr, int(mo.group(2)))

def gtkwave_tcl(cmd):
    p = gtkwave_socket_param(gdb.parameter("gtkwave-socket"))
    if p is None:
        raise gdb.GdbError('gtkwave-socket parameter is unset')
    s = socket.socket()
    s.connect(p)
    s.send((cmd + "\n").encode("ascii"))
    s.close()

class GtkWaveSocketParam(gdb.Parameter):
    """GtkWave control socket."""

    def __init__(self):
        self.show_doc = "GtkWave control socket."
        self.set_doc = "GtkWave control socket (eg 'localhost:1234')"
        super(GtkWaveSocketParam, self).__init__("gtkwave-socket",
                gdb.COMMAND_DATA, gdb.PARAM_STRING)
        self.value = os.getenv("GTKWAVE_CONTROL_SOCKET")
        self.saved_value = self.value

    def validate(self):
        if gtkwave_socket_param(self.value) is None:
            return False
        return True

    def get_set_string(self):
        if not self.validate():
            self.value = self.saved_value
            raise gdb.GdbError('Bad value')
        self.saved_value = self.value
        return self.value

class GtkWaveTclCommand(gdb.Command):
    """Execute a tcl command in gtkwave embedded interpreter."""
    def __init__(self):
            super(GtkWaveTclCommand, self).__init__("gtkwave-tcl",
                    gdb.COMMAND_USER)

    def invoke(self, argv, from_tty):
        gtkwave_tcl(argv)

class GtkWaveSetTime(gdb.Command):
    """Set the current time of the gtkwave viewer.
It takes one argument which is the absolute timestamp: it is a number
eventually followed by a time unit suffix (eg: '50', '100s', '12ms', ).
Special keyword argument 'start' and 'end' are also supported."""
    def __init__(self):
            super(GtkWaveSetTime, self).__init__("gtkwave-set-time",
                    gdb.COMMAND_USER)

    def invoke(self, argv, from_tty):
        if len(argv.split()) != 1:
            raise gdb.GdbError('gtkwave-set-time takes one argument')
        if argv == 'start':
            gtkwave_tcl("gtkwave::/Time/Zoom/Zoom_To_Start")
        elif argv == 'end':
            gtkwave_tcl("gtkwave::/Time/Zoom/Zoom_To_End")
        else:
            gtkwave_tcl("gtkwave::setWindowStartTime {}".format(argv))

class GtkWaveToggleDynTime(gdb.Command):
    """Toggle the dynamic time setting. When it is enabled the gtkwave
view follows the end while the trace if generated."""
    def __init__(self):
            super(GtkWaveToggleDynTime, self).__init__("gtkwave-toggle-dyn-time",
                    gdb.COMMAND_USER)

    def invoke(self, argv, from_tty):
        if len(argv.split()) != 0:
            raise gdb.GdbError('gtkwave-toggle-dyn-time takes no argument')
        gtkwave_tcl("gtkwave::/View/Partial_VCD_Dynamic_Zoom_To_End")

GtkWaveSocketParam()
GtkWaveTclCommand()
GtkWaveSetTime()
GtkWaveToggleDynTime()
