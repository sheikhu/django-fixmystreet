$INSTALL_ROOT=/home/fixmystreet/django-fixmystreet
chown -R fixmystreet:fixmystreet $INSTALL_ROOT
sudo -u fixmystreet $INSTALL_ROOT/bin/django clear_cache
sudo -u fixmystreet $INSTALL_ROOT/bin/django syncdb --migrate
