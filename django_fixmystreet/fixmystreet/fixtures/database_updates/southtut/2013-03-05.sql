update fixmystreet_organisationentity set name_fr='Auderghem', name_nl='Oudergem' where phone = '02/676.48.11';
update fixmystreet_organisationentity set name_fr='Berchem-Sainte-Agathe', name_nl='Sint-Agatha-Berchem' where phone = '02/464.04.11';
update fixmystreet_organisationentity set name_fr='Bruxelles-ville', name_nl='Brussel stad' where phone = '02/279.22.11';
update fixmystreet_organisationentity set name_fr='Evere', name_nl='Evere' where phone = '02/247.62.62';
update fixmystreet_organisationentity set name_fr='Anderlecht', name_nl='Anderlecht' where phone = '02/558.08.00';
update fixmystreet_organisationentity set name_fr='Etterbeek', name_nl='Etterbeek' where phone = '02/627.21.11';
update fixmystreet_organisationentity set name_fr='Ixelles', name_nl='Elsene' where phone = '02/515.61.11';
update fixmystreet_organisationentity set name_fr='Forest', name_nl='Vorst' where phone = '02/370.22.11';
update fixmystreet_organisationentity set name_fr='Ganshoren', name_nl='Ganshoren' where phone = '02/465.12.77';
update fixmystreet_organisationentity set name_fr='Jette', name_nl='Jette' where phone = '02/423.12.11';
update fixmystreet_organisationentity set name_fr='Molenbeek Saint Jean', name_nl='Sint-Jans-Molenbeek' where phone = '02/412.36.75';
update fixmystreet_organisationentity set name_fr='Saint-Josse-ten-Noode', name_nl='Sint-Joost-ten-Node' where phone = '02/220.26.11';
update fixmystreet_organisationentity set name_fr='Koekelberg', name_nl='Koekelberg' where phone = '02/412.14.11';
update fixmystreet_organisationentity set name_fr='Saint-Gilles', name_nl='Sint-Gillis' where phone = '02/536.02.11';
update fixmystreet_organisationentity set name_fr='Schaerbeek', name_nl='Schaarbeek' where phone = '02/244.75.11';
update fixmystreet_organisationentity set name_fr='Woluwe Saint Lambert', name_nl='Sint-Lambrechts-Woluwe' where phone = '02/761.27.11';
update fixmystreet_organisationentity set name_fr='Uccle', name_nl='Ukkel' where phone = '02/348.65.11';
update fixmystreet_organisationentity set name_fr='Watermael-Boitsfort', name_nl='Watermaal-Bosvoorde' where phone = '02/674.74.11';
update fixmystreet_organisationentity set name_fr='Woluwe Saint Pierre', name_nl='Sint-Pieters-Woluwe' where phone = '02/773.05.11';

update fixmystreet_listitem set label_fr='syndic d''immeuble', label_nl='gebouw Beheerder' where model_field='quality' and code = '3';
update fixmystreet_listitem set label_fr='autre', label_nl='andere' where model_field='quality' and code = '1';

update fixmystreet_reportsecondarycategoryclass set name_fr='Revêtement' where name_nl='Beschadigingen';

INSERT INTO south_migrationhistory(app_name, migration, applied)
    VALUES ('fixmystreet','0001_initial','2013-03-06 09:04:17.015097+01');
