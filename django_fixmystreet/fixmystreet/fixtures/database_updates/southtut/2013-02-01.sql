alter table fixmystreet_organisationentity add column active boolean NOT NULL DEFAULT false;

update fixmystreet_organisationentity o set active = true where exists (select * from fixmystreet_fmsuser where manager=true and organisation_id=o.id);

delete from fixmystreet_reportfile where file_type = 4;
alter table fixmystreet_reportfile add column image character varying(100) NULL; 
