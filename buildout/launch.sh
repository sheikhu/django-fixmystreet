#!/bin/bash

cd "$( dirname "${BASH_SOURCE[0]}" )"

APP="fixmystreet"
echo "launching app $APP"

case "$1" in
  jenkins)
    CONF="jenkins.cfg"
    ;;
  *)
    CONF="dev.cfg"
    ;;
esac
echo "buildout using $CONF"


if [[ ! -d bin ]]
then
    python2.6 bootstrap.py -c $CONF
fi
bin/buildout -c $CONF -Nvt 5

PG_EXISTS=0
PG_DOWN=0
if [ -f bin/pg_ctl ]
then
    echo "postgres is installed using buildout"
    PG_EXISTS=1

    ps -C postgres 1> /dev/null
    PG_DOWN=$? # $? == 1 if no process postgres is found

    if [ $PG_DOWN ]
    then
        echo "postgres is down, start postgres"
        bin/pg_start
    fi
fi

case "$1" in
  jenkins)
    bin/django-jenkins $APP
    ;;
  test)
    bin/django test $APP
    ;;
  debug)
    bin/django-debug runserver
    ;;
  *)
    bin/django runserver
    ;;
esac

if [[ $PG_EXISTS != 0 && $PG_DOWN != 0 ]]
then
    echo "postgres was started, shutdown postgres"
    bin/pg_stop
fi
