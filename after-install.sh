chown -R fixmystreet:fixmystreet /home/fixmystreet/django-fixmystreet
sudo -u fixmystreet bin/django clear_cache
sudo -u fixmystreet bin/django syncdb --migrate
