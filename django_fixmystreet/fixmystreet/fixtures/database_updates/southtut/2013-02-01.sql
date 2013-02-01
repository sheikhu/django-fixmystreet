alter table fixmystreet_organisationentity add column active boolean NOT NULL DEFAULT false;

update fixmystreet_organisationentity o set active = true where exists (select * from fixmystreet_fmsuser where manager=true and organisation_id=o.id);
