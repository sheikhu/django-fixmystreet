
BEGIN;

CREATE OR REPLACE VIEW ods_incident_event AS SELECT
    r.id,
    r.history_id,
    r.history_date,
    r.history_type,
    CASE
        WHEN (r.status IS NOT NULL) THEN r.status::int
        ELSE 0
    END as status,
    CASE
        WHEN (r.status=1 OR r.status=9) THEN 'created'
        WHEN (r.status=3 OR r.status=8) THEN 'processed'
        ELSE 'in_progress'
    END as main_status,
    CASE
        WHEN (citizen.quality IS NOT NULL) THEN citizen.quality::int
        ELSE 0
    END as quality,
    r.point,
    r.address_fr as street_name_fr,
    r.address_nl as street_name_nl,
    r.postalcode as postalcode,
    r.address_number as address_number,
    created_by.organisation_id as created_by_entity_id,
    CASE
        WHEN (r.created_by_id IS NULL AND r.citizen_id IS NOT NULL) THEN r.citizen_id
        WHEN (r.created_by_id IS NULL) THEN -1
        ELSE r.created_by_id
    END as created_by_user_id,
    CASE
        WHEN (r.responsible_entity_id IS NULL) THEN -1
        ELSE r.responsible_entity_id
    END as responsible_entity_id,
    r.responsible_department_id as responsible_manager_id,
    -- CASE
    --     WHEN (r.responsible_department_id IS NOT NULL) THEN r.responsible_department_id
    --     ELSE 100000 + r.responsible_manager_id
    -- END as responsible_manager_id,
    CASE
        WHEN (r.contractor_id IS NULL) THEN 0
        ELSE r.contractor_id
    END as contractor_id,
    r.private,
    r.created_by_id IS NOT NULL as is_pro,
    r.category_id,
    category.secondary_category_class_id,
    r.secondary_category_id,
    zipcode.commune_id as territorial_entity,
    (
        SELECT count(att_com.id) FROM fixmystreet_reportattachment att_com
            JOIN fixmystreet_reportcomment com ON att_com.id=com.reportattachment_ptr_id
            WHERE att_com.report_id=r.id
    ) as comments_count,
    (
        SELECT count(att_photo.id) FROM fixmystreet_reportattachment att_photo
            JOIN fixmystreet_reportfile photo ON att_photo.id=photo.reportattachment_ptr_id
            WHERE att_photo.report_id=r.id AND file_type=4
    ) as photos_count,
    r.merged_with_id
FROM fixmystreet_historicalreport r
    RIGHT JOIN fixmystreet_report original_report ON r.id=original_report.id
    LEFT JOIN fixmystreet_fmsuser created_by ON r.created_by_id=created_by.user_ptr_id
    LEFT JOIN fixmystreet_fmsuser citizen ON r.citizen_id=citizen.user_ptr_id
    LEFT JOIN fixmystreet_reportcategory category ON r.secondary_category_id=category.id
    LEFT JOIN fixmystreet_zipcode zipcode ON r.postalcode=zipcode.code
    WHERE original_report.merged_with_id IS NULL;
    ;
--     LEFT JOIN fixmystreet_historicalreport previous_row ON previous_row.history_id = (
--         SELECT Max(previous_rows.history_id)
--             FROM fixmystreet_historicalreport previous_rows
--             WHERE previous_rows.history_id < r.history_id AND r.id=previous_rows.id
--         )
-- WHERE previous_row.id IS NULL OR r.status != previous_row.status OR r.responsible_manager_id != previous_row.responsible_manager_id;


CREATE OR REPLACE VIEW ods_dim_status AS SELECT
    code::int,
    label_fr,
    label_nl
FROM fixmystreet_listitem
    WHERE model_class='fixmystreet.report'
    AND model_field='status';


CREATE OR REPLACE VIEW ods_dim_user AS SELECT
    ID,
    CASE WHEN (first_name != '')
        THEN first_name || ' ' || last_name
        ELSE last_name
    END as user_name,
    agent as agent_flag,
    manager as manager_flag,
    leader as entity_flag
FROM fixmystreet_fmsuser fmsuser
    LEFT JOIN auth_user u ON user_ptr_id=u.id;


CREATE OR REPLACE VIEW ods_dim_manager AS SELECT
    ID,
    name_fr || ' / ' || name_nl as user_name,
    FALSE as agent_flag,
    TRUE as manager_flag,
    FALSE as entity_flag
FROM fixmystreet_organisationentity manager
    WHERE type='D';


CREATE OR REPLACE VIEW ods_dim_quality AS SELECT
    code::int,
    label_fr,
    label_nl
FROM fixmystreet_listitem
    WHERE model_class='fixmystreet.report'
    AND model_field='quality';


CREATE OR REPLACE VIEW ods_dim_entity_responsible AS SELECT
    id,
    name_fr,
    name_nl,
    type='C' as commune,
    type='R' as region,
    slug_fr,
    slug_nl
FROM fixmystreet_organisationentity
WHERE type='C' OR type='R';

CREATE OR REPLACE VIEW ods_dim_entity_contractor AS SELECT
    id,
    name_fr,
    name_nl,
    type='S' as subcontractor,
    type='A' as applicant,
    slug_fr,
    slug_nl
FROM fixmystreet_organisationentity
    WHERE type='S' OR type='A';


CREATE OR REPLACE VIEW ods_dim_category AS SELECT
    id,
    name_fr,
    name_nl,
    secondary_category_class_id,
    category_class_id
FROM fixmystreet_reportcategory;


CREATE OR REPLACE VIEW ods_dim_main_category_class AS SELECT
    id,
    name_fr,
    name_nl
FROM fixmystreet_reportmaincategoryclass;


CREATE OR REPLACE VIEW ods_dim_secondary_category_class AS SELECT
    id,
    name_fr,
    name_nl
FROM fixmystreet_reportsecondarycategoryclass;

COMMIT;