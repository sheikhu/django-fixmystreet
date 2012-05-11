#!/bin/bash

CURRENT_DIR="$( dirname "${BASH_SOURCE[0]}" )"

APP="fixmystreet"
echo "--launching $1 $APP"

case "$1" in
  jenkins)
    $CURRENT_DIR/bin/django-jenkins jenkins $APP
    # rpm
    ;;
  test)
    $CURRENT_DIR/bin/django test $APP
    ;;
  debug)
    $CURRENT_DIR/bin/django-debug runserver
    ;;
  *)
    $CURRENT_DIR/bin/django runserver
    ;;
esac

