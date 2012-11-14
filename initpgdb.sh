#!/bin/bash -x

USER=fixmystreet
DBNAME=fixmystreet-thibaut

if [ -f ./bin/pg_ctl ]
then
	echo "postgres is installed using buildout"
	export PATH="./bin":$PATH
fi

psql -l -U $USER | grep -q $DBNAME
if [ $? -ne 0 ]
then
	echo "Creating $USER user"
	createuser -S -d -R $USER
	psql -d postgres -c "ALTER USER $USER PASSWORD '';"

	echo "Creating $DBNAME db"
	createdb $DBNAME -U $USER -T template_postgis
fi
