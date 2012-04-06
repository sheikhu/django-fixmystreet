#!/bin/bash

cd "$( dirname "${BASH_SOURCE[0]}" )"

APP="fixmystreet"
echo "--launching $1 $APP"

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

