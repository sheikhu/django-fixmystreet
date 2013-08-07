DROP VIEW ods_incident_event;
DROP VIEW ods_dim_status;
DROP VIEW ods_dim_user;
DROP VIEW ods_dim_manager;
DROP VIEW ods_dim_quality;
DROP VIEW ods_dim_entity_responsible;
DROP VIEW ods_dim_entity_contractor;


CREATE OR REPLACE VIEW ods_incident_event AS SELECT
    r.id,
    r.history_id,
    r.history_date,
    r.history_type,
    r.status,
    CASE
        WHEN (status=1 OR status=9) THEN 'created'
        WHEN (status = 3 OR status=8) THEN 'processed'
        ELSE 'in_progress'
    END as main_status,
    r.quality,
    r.point,
    r.address_fr as street_name_fr,
    r.address_fr as street_name_nl,
    created_by.organisation_id as created_by_entity_id,
    r.created_by_id as created_by_user_id,
    r.responsible_entity_id,
    r.responsible_manager_id,
    r.contractor_id,
    r.private,
    r.created_by_id IS NOT NULL as is_pro,
    r.category_id,
    category.category_class_id,
    r.secondary_category_id,
    (
        SELECT count(att_com.id) FROM fixmystreet_reportattachment att_com
            LEFT JOIN fixmystreet_reportcomment com ON att_com.id=com.reportattachment_ptr_id
            WHERE att_com.report_id=r.id
    ) as comments_count,
    (
        SELECT count(att_photo.id) FROM fixmystreet_reportattachment att_photo
            LEFT JOIN fixmystreet_reportfile photo ON att_photo.id=photo.reportattachment_ptr_id
            WHERE att_photo.report_id=r.id AND file_type=4
    ) as photos_count
FROM fixmystreet_historicalreport r
    LEFT JOIN fixmystreet_fmsuser created_by ON r.created_by_id=created_by.user_ptr_id
    LEFT JOIN fixmystreet_reportcategory category ON r.category_id=category.id;


CREATE OR REPLACE VIEW ods_dim_status AS SELECT
    code,
    label_fr,
    label_nl
FROM fixmystreet_listitem
    WHERE model_class='fixmystreet.report'
    AND model_field='status';


CREATE OR REPLACE VIEW ods_dim_user AS SELECT
    concat(first_name, ' ', last_name) as user_name,
    agent as agent_flag,
    manager as manager_flag,
    leader as entity_flag
FROM fixmystreet_fmsuser fmsuser
    LEFT JOIN auth_user u ON user_ptr_id=u.id
    WHERE agent OR manager OR leader;



CREATE OR REPLACE VIEW ods_dim_manager AS SELECT
    concat(first_name, ' ', last_name) as user_name,
    agent as agent_flag,
    manager as manager_flag,
    leader as entity_flag
FROM fixmystreet_fmsuser fmsuser
    LEFT JOIN auth_user u ON user_ptr_id=u.id
    WHERE manager;


CREATE OR REPLACE VIEW ods_dim_quality AS SELECT
    code,
    label_fr,
    label_nl
FROM fixmystreet_listitem
    WHERE model_class='fixmystreet.report'
    AND model_field='quality';


CREATE OR REPLACE VIEW ods_dim_entity_responsible AS SELECT
    id,
    name_fr,
    name_nl,
    commune,
    region
FROM fixmystreet_organisationentity
WHERE active AND (commune OR region)

CREATE OR REPLACE VIEW ods_dim_entity_contractor AS SELECT
    id,
    name_fr,
    name_nl,
    subcontractor,
    applicant
FROM fixmystreet_organisationentity
WHERE subcontractor OR applicant;


ods_dim_main_category
    id
    name_fr
    name_nl

ods_dim_secondary_category_class
    id
    name_fr
    name_nl

ods_dim_category
    id
    name_fr
    name_nl
    main_category
    secondary_category_class
