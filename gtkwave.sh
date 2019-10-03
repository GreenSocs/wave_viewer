#!/bin/bash

if [[ "$#" == 0 || "$1" =~ ^-.*$ ]]
then
    echo "usage:$0 trace_file [gtkwave options ...]" >&2
    exit 1
fi

trace=$1
shift
gtkwave=gtkwave
shmidcat=shmidcat

if [ -n "$GTKWAVE_PATH" ]
then
    gtkwave=${GTKWAVE_PATH}/gtkwave
    shmidcat=${GTKWAVE_PATH}/shmidcat
fi

if [ ! -e "$trace" ]
then
    echo "Trace file '$trace' does not exist"
    echo "Attempting to create it..."
    mkdir -p $(dirname "$trace") || exit 1
    mkfifo "$trace" || exit 1
    echo "Trace file successfully created."
fi
if [ ! -p "$trace" ]
then
    echo "Warning: '$trace' is not a pipe, live view will not work properly"
fi

# kill coporoc on sigterm
# so that no pending process remain
gtkwave_pid=
COPROC_PID=
term()
{
    if [ -n "${COPROC_PID}" ]
    then
        echo "Terminating shmidcat process"
        if kill -0 ${COPROC_PID} 2>/dev/null
        then
            kill -9 "${COPROC_PID}"
        fi
    fi
    if [ -n "${gtkwave_pid}" ]
    then
        echo "Terminating gtkwave process"
        if kill -0 ${gtkwave_pid} 2>/dev/null
        then
            kill -9 "${gtkwave_pid}"
        fi
    fi
    exit 0
}
trap 'term' SIGTERM SIGINT

# run shmidcat in background but gets 1st stdout line which contains
# the shared memory id
# shmidcat will stop when the tracing side stops iff trace has been started
echo "Opening the trace file '$trace'."
coproc $shmidcat $trace
echo "Waiting for shared memory creation..."
read SHMID <&${COPROC[0]}

# launch gtkwave if we got an ID
if [[ -n "$SHMID" ]]
then
    echo "Created shared memory trace with id $SHMID"
    echo "Starting $gtkwave -I $SHMID $@"
    $gtkwave -I $SHMID "$@" &
    gtkwave_pid=$!
    wait
else
    echo "Failed to create shared memory trace." >&2
    exit 1
fi

