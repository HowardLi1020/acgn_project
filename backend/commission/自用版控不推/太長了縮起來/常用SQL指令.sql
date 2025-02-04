drop database shopping;
create database shopping;
use shopping;

-- drop table member_basic;
drop table db_need_info;
-- drop table db_need_images;
-- drop table db_works_info;
-- drop table db_works_preview;
drop table db_public_card_info;
drop table db_public_card_sell;

SELECT * FROM shopping.member_basic;
SELECT * FROM shopping.db_need_info;
SELECT * FROM shopping.db_need_images;
SELECT * FROM shopping.db_works_info;
SELECT * FROM shopping.db_works_preview;
SELECT * FROM shopping.db_public_card_info;
SELECT * FROM shopping.db_public_card_sell;

UPDATE db_public_card_info
SET 
    user_nickname = 'A漫',
    card_status = '公開'
WHERE 
    user_nickname = '阿曼答'
    AND card_status = '非公開';

UPDATE db_public_card_info
SET 
    sell_public_status = false,
    work_list_public_status = 1,
    work_done_list_public_status = 1,
    need_list_public_status = false
WHERE 
    user_id IN (4);

-- data 先
-- py manage.py inspectdb shopping db_need_info db_need_images db_works_info works_preview db_public_card_info db_public_card_sell > commission/models.py

-- code 先
-- python manage.py makemigrations commission
-- python manage.py migrate commission