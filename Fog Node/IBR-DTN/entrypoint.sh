#!/bin/sh

if [ ! -f /dtn.conf ] ; then
    mv /dtn-default.conf /dtn.conf
fi

exec "$@"