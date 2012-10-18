chown -R ibsa:ibsa /home/ibsa/Monitoring-Des-Quartiers
sudo -u ibsa ln -fs /data/ibsa/attachments /home/ibsa/Monitoring-Des-Quartiers/src/static/attachments
sudo -u ibsa /home/ibsa/Monitoring-Des-Quartiers/bin/django-deploy clear_cache
#sudo -u ibsa /home/ibsa/Monitoring-Des-Quartiers/bin/django-deploy syncdb --migrate
