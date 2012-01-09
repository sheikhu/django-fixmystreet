ALTER TABLE mainapp_ward DROP COLUMN number;
ALTER TABLE mainapp_ward ADD COLUMN feature_id varchar(25) DEFAULT '' NOT NULL;

ALTER TABLE mainapp_report DROP COLUMN point;
ALTER TABLE mainapp_report ADD COLUMN point geometry;
