
# Wave viewer eclipse project

This is an example eclipse project adding live wave viewer into an eclipse
workspace.

## Requirements

* An Eclipse CDT (C/C++ development). If is not packaged in your distrbution,
  you can download it from the eclipse
  [website](https://www.eclipse.org/downloads/packages/). Choose **Eclipse IDE
  for C/C++ Developers**. It works with 2019.6 or 2019.9 version.

* The **XEmbedPlugin** into your eclipse installation. It is available in this
  [repository](https://github.com/GreenSocs/XEmbedEclipsePlugin). You can
  follow the step in the README to install it. This plug-in is optional, see
  _Using this project without the embedded viewer_ below to use the project
  without it.

* **Gtkwave** program with tcl support and an additional tcl socket support. It is
  available in this [repository](https://github.com/GreenSocs/gtkwave). Follow
  the step in the README to build and install it. This gtkwave install directory
  must be in your PATH. It also possible to use this project without special
  gtkwave, see _Using this project without custom gtkwave_ below for more information.

* **gdb-multiarch** debugger. It can work with any packaged gdb with aarch64
  architecture support: see _Using this project with another gdb_.

## Setup

### 1. Import `wave_viewer` project.

Open an eclipse workspace. You need to add this project into it.
First copy the project files into your disk.
Then in Eclipse, in the menu **File** -> **Import...** window.
Select **General** -> **Existing project into workspace** and hit **Next**
button. You have to select the directory where this project is. Ensure 
`wave_viewer` project is selected in the list then hit **Finish** button.

### 2. Import `linux-aarch64` project

This project is configured to go along with a project named `linux-aarch64`
which should contain a compiled linux kernel source tree with the generated 
vmlinux elf file.

### 3. Initialize the trace file

You also need to create a named pipe file that will be used for exchanging
data between the simulation and the viewer.

In the directory containing the `wave_viewer` project (where you cloned or copied it), do:
```
mkfifo trace.vcd
```

## Launch configurations

The project adds 3 launch configurations:
1. _gtkwave_ launch the wave viewer,
2. _linux-aarch64 debug_ the debugger on remote mode for the linux kernel,
3. and _gdb and wave_ which launch them both.

We use the last one to launch everything at the same time.
In the launch configuration dropdown list, select **gdb and wave**.
Then in the dropdown menu at the left, select **debug** mode. This last step is
important.

You launch the configuration using the **Launch in 'Debug' mode** button (middle
button at the left of the drop-down with a small bug icon).
Then it starts the debugger session and the viewer.

The viewer is displayed in an eclipse view that is named XEmbedView. At first
it is added in a tab with all the other views along with the debugger console.
You can then move it to some other place in your persepective.
If the tab does not appear the first time you launch it, you need to add it
manually using the following steps:
1. Go in the **Window** menu -> **Show View** -> **Other...**
2. In **General** folder, select **XEmbedView**, then hit **Open** button.

## Using this project without the embedded viewer

It is possible to use this project without having the wave viewer embedded into
eclipse perspective. In that case you don't need the XEmbedPlugin.

To disable it, just edit the **gtkwave** launch configuration. You have to remove the
`-X ${xembed_window_id}` from the argument list. Gtkwave will then open in a
separate window in your graphical environment.

## Using this project without custom gtkwave

To use this project with standard gtkwave, you need to edit the _gtkwave_
launch configuration. In the argument list, remove the `-p 6789` line.
You wont'be able to control gtkwave from gdb console.

If your gtkwave does not support tcl. You need also to remove the `-S init.tcl`
arguments.

## Using this project with another gdb

This project is configured to use _gdb-multiarch_. You need to modify the
_linux-aarcg64 debug_ launch configuration to change the debugger program if
you want to use another one.

When you edit the configuration, select the **debugger** tab and update the
**GDB debugger** entry.

## GDB commands

This project contains the `gtkwave-gdb.py` file which is loaded by gdb (it is
configured in the `linux-aarch64 debug` launch configuration).
This module adds 2 commands.

### gtkwave-set-time

It sets the current time displayed in gtkwave view. It takes one argument
specifying the timestamp. The timestamp can be the keywords _start_ or _end_
or a number with a time unit.

Examples:

```
gtkwave-set-time start
gtkwave-set-time end
gtkwave-set-time 32s
gtkwave-set-time 42ms
gtkwave-set-time 18
```

### gtkwave-toggle-dyn-time

It toggles the dynamic displaying in gtkwave view. It take no argument.
When it is enabled the view show the last generated trace while generation.

Example:
```
gtkwave-toggle-dyn-time
```

### Control socket

GTKWave is controlled using a socket. It needs to be configured in gdb so that
the new commands work. This project use the default port 6789 but it can be
changed.

The module adds a new gdb parameter named _gtkwave-socket_. It can be displayed
and changed using the `show gtkwave-socket` and `set gtkwave-socket host:port`
commands.

This parameter is initialized with the content of `GTKWAVE_CONTROL_SOCKET`
environment variable or default to 6789.

Note that if you change the port in gdb, you also need to change the port
configured in the gtkwave command line.

