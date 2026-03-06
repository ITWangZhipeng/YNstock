DELETE
FROM bizops.t_def_data_collect
WHERE collection_definition_key = 'guarantee_interest_collect';
DELETE
FROM bizops.t_def_index
WHERE index_definition_key = 'guarantee_interest_amount';
DELETE
FROM bizops.t_def_checker
WHERE checker_definition_key = 'SD_INTEREST_CHECK';
INSERT INTO bizops.t_def_data_collect (collection_definition_key, collection_definition_name, collect_type, source_db,
                                       db_name, db_schema, db_sql, result_field, create_timestamp)
VALUES ('guarantee_interest_collect', '担保金结息（全市场）', 'sql', 'Hive', 'settle', 'settle',
        'select money_in,money_out,settle_member_id from settle.t_money_io', 'money_in,money_out,settle_member_id',
        CURRENT_TIMESTAMP);
INSERT INTO bizops.t_def_index (index_definition_key, index_definition_name, index_type, cal_expression, cal_type,
                                description, responsible_dept_id, responsible_position_id, developer,
                                task_lifecycle_status, result_field)
VALUES ('guarantee_interest_amount', '担保金结息金额', 'atomic',
        '{"expression": "money_in - money_out", "result_field": "net_interest"}', 'expression',
        '计算担保金净结息金额（收入减支出）', 'JSB', 'JSBJSG', '王志鹏', '1', 'net_interest');
INSERT INTO bizops.t_def_checker (checker_definition_key, checker_definition_name, category_key, description,
                                  responsible_dept_id, responsible_position_id, developer, cal_expression, task_type,
                                  task_lifecycle_status)
VALUES ('SD_INTEREST_CHECK', '担保金变动异构稽核', '结算稽核', '检查担保金解析结果与系统记录是否一致', 'JSB', 'JSBJSG',
        '王志鹏', 'guarantee_interest_amount', 'INDEX', '1');