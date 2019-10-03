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

# initialize a new named pipe
#rm -f $trace
#mkfifo $trace

# kill coporoc on sigterm
# so that no pending process remain
gtkwave_pid=
COPROC_PID=
term()
{
    if [ -n "${COPROC_PID}" ]
    then
        echo "Terminating shmidcat process" >&2
        if kill -0 ${COPROC_PID} 2>/dev/null
        then
            kill -9 "${COPROC_PID}"
        fi
    fi
    if [ -n "${gtkwave_pid}" ]
    then
        echo "Terminating gtkwave process" >&2
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
# shmidcat will stop when systemc stops iff trace has been started
coproc $shmidcat $trace
read SHMID <&${COPROC[0]}

# launch gtkwave if we got an ID
if [[ -n "$SHMID" ]]
then
    echo "Got shmidcat id $SHMID"
    echo "starting $gtkwave -I $SHMID $@"
    $gtkwave -I $SHMID "$@" &
    gtkwave_pid=$!
    wait
else
    echo "Shmidcat failed" >&2
fi

#rm -f $trace
