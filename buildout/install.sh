#!/bin/bash

CURRENT_DIR="$( dirname "${BASH_SOURCE[0]}" )"

APP="fixmystreet"
echo "--installing app $APP"

case "$1" in
  sync)
    $CURRENT_DIR/bin/django syncdb --noinput
    $CURRENT_DIR/bin/django migrate
    exit 0
    ;;
  jenkins)
    CONF="jenkins.cfg"
    ;;
  *)
    CONF="dev.cfg"
    ;;
esac

echo "--buildout using $CONF"
if [[ ! -d bin ]]
then
    python2.6 bootstrap.py -c $CONF
fi
$CURRENT_DIR/bin/buildout -c $CONF -Nvt 5
echo "end of buildout!"


echo "--sync db"
$CURRENT_DIR/bin/django syncdb --noinput
$CURRENT_DIR/bin/django migrate

