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
echo "end of buildout!"

bin/django syncdb --noinput
bin/django migrate


case "$1" in
  jenkins)
    bin/django-jenkins jenkins $APP
    # rpm
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

