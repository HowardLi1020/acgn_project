-- 管理者帳號密碼
insert into auth_user(superuser_name, superuser_email,superuser_password)
values
('superuser','superuser@gmail.com', '1234qwer'),
('admin','admin@gmail.com', '1234qwer');

-- 會員假資料
insert into member_basic(user_name, user_password, user_phone, user_email, user_nickname, user_gender, user_birth)
values
('Amanda', '1234qweasd', '0912123128', 'Amanda@gmail.com', '阿曼答', 'female', '1996-10-15'),
('Brian', '1234qweasd', '0912123127', 'Brian@gmail.com', '布萊恩', 'male', '2000-01-15'),
('Cally', '1234qweasd', '0912123126', 'Cally@gmail.com', '可立', 'female', '1999-12-15'),
('Daniel', '1234qweasd', '0912123125', 'Daniel@gmail.com', '丹尼', 'prefer_not_to_say', '1986-03-29'),
('Eddie', '1234qweasd', '0912123124', 'Eddie@gmail.com', '艾迪', 'male', '2012-02-10'),
('Jessica', '1234qweasd', '0912123123', 'Jessica@gmail.com', '潔西卡', 'female', '1987-10-26'),
('Ashley', '1234qweasd', '0912345673', 'Ashley@gmail.com', '愛須', 'prefer_not_to_say', '1988-12-15'),
('Jay', '1234qweasd', '0912345672', 'forworkjayjay@gmail.com', '杰', 'prefer_not_to_say', '2000-11-11'),
('Rosa', '1234qweasd', '0912345671', 'Rosa@gmail.com', '蘿莎', 'female', '1988-10-15'),
('Jeremy', '1234qweasd', '0912345670', 'yuhaohong@gmail.com', '傑若米', 'male', '1987-08-22'),
('Monica', '1234qweasd', '0912345600', 'Monica@gmail.com', '莫妮卡', 'female', '2012-03-30');

-- 插入品牌資料 (動漫相關品牌)
INSERT INTO product_brands (brand_name) VALUES 
('Good Smile Company'),
('BANPRESTO'),
('TAKARA TOMY');

-- 插入系列資料 (動漫系列)
INSERT INTO product_series (series_name) VALUES 
('進擊的巨人'),
('鬼滅之刃'),
('ONE PIECE');

-- 插入類別資料 (商品類別)
INSERT INTO product_categories (category_name) VALUES 
('公仔'), 
('模型'),
('鑰匙圈');

-- 插入商品資料 (動漫周邊商品)
INSERT INTO products (user_id, product_name, description_text, brand_id, series_id, category_id, price, stock) VALUES 
(1, '艾倫·葉卡 公仔', '來自《進擊的巨人》的艾倫公仔，精緻還原。', 1, 1, 1, 900, 50),
(2, '炭治郎 模型', '《鬼滅之刃》炭治郎1/8比例模型，適合收藏。', 2, 2, 2, 1500, 30),
(3, '魯夫 鑰匙圈', '《ONE PIECE》的魯夫Q版鑰匙圈，可愛又實用。', 3, 3, 3, 199, 100),
(1, '三笠 公仔', '來自《進擊的巨人》的三笠公仔，忠實呈現細節。', 1, 1, 1, 899, 40),
(2, '禰豆子 模型', '《鬼滅之刃》禰豆子精緻模型，細節一流。', 2, 2, 2, 1399, 25),
(3, '索隆 鑰匙圈', '《ONE PIECE》的索隆鑰匙圈，帶有劍士風格。', 3, 3, 3, 249, 80);

-- 插入商品圖片資料
INSERT INTO product_images (product_id, image_url, is_main) VALUES 
(1, 'products/aot_eren_main.jpg', TRUE),
(1, 'products/aot_eren_1.jpg', FALSE),
(2, 'products/knys_tanjiro_main.jpg', TRUE),
(3, 'products/op_luffy_keychain.jpg', TRUE),
(4, 'products/aot_mikasa_main.jpg', TRUE),
(5, 'products/knys_nezuko_main.jpg', TRUE),
(6, 'products/op_zoro_keychain.jpg', TRUE);

-- 五、委託
SET FOREIGN_KEY_CHECKS = 0;
-- 5-1 需求案假資料
INSERT INTO db_need_info (needer_id, need_title, need_category, need_original_from, need_description, need_price, publish_time, deadline, last_update, need_status, public_status) VALUES
(10, '時尚耳環產品圖設計', '平面設計', '刀劍亂舞', '需要為我們最新系列的5款耳環設計產品展示圖。希望風格簡約現代，突出耳環的設計感。背景需要能襯托出耳環的特色，可以考慮使用柔和的漸變色。', 3000, '2024-09-13 10:00:00', '2024-09-20 18:00:00', '2024-09-13 10:00:00', '徵件中', TRUE),
(2, '遊戲實況用動態頭像', '動畫設計', '三麗鷗 凱蒂貓', '需要一個有趣的動態頭像用於我的遊戲實況。希望是一隻可愛的卡通貓咪形象，能有簡單的動作，如眨眼、點頭等。最好能配合我直播時的情緒有些變化，例如高興時貓咪笑、驚訝時貓咪睜大眼睛等。', 5000, '2024-09-14 14:30:00', '2024-09-28 23:59:59', '2024-09-14 14:30:00', '徵件中', FALSE),
(10, '遊戲角色設計', '遊戲美術', '魔法少女小圓', '需要設計遊戲的主角，一位16歲的魔法少女。她應該有標誌性的武器和服裝。風格要偏向二次元，但也要有自己的特色。需要正面、側面和背面的設計圖，以及幾個常用動作的草圖。', 10000, '2024-09-22 11:30:00', '2024-10-22 18:00:00', '2024-09-22 11:30:00', '截止', FALSE),
(3, '讀書會海報設計', '平面設計', '無', '需要一張富有創意的海報來宣傳我們即將舉辦的科幻主題讀書會。希望海報能融入書本、星球、宇宙飛船等元素，色彩要豐富吸睛。海報上需要包含活動名稱、時間、地點和一句富有哲理的科幻名言。', 1500, '2024-09-15 09:15:00', '2024-09-22 21:00:00', '2024-09-15 09:15:00', '已成交', TRUE),
(10, '海洋生物插畫集', '科學插畫', '無', '需要繪製20種深海生物的精細插畫，包括一些罕見的發光生物。每幅插畫都需要準確反映生物的特徵，並配有簡單的解剖圖。風格要科學精準，但也要保持一定的藝術美感。', 20000, '2024-09-23 09:00:00', '2024-11-23 23:59:59', '2024-09-23 09:00:00', '徵件中', TRUE),
(4, '教育回憶錄書籍封面', '書籍裝幀', '原創', '需要為我的教育回憶錄設計封面。書名是《粉筆與黑板的歲月》。希望封面能體現出教育的溫度，可以考慮使用一些象徵性的元素，如粉筆、書本、黑板等。色調偏向溫暖懷舊，但不要太過老氣。', 2500, '2024-09-16 11:00:00', '2024-09-30 18:00:00', '2024-09-16 11:00:00', '取消徵件', FALSE),
(5, '智能音箱產品渲染圖', '3D建模與渲染', '無', '需要為我們即將推出的智能音箱製作一張高質量的產品渲染圖。音箱的設計理念是簡約現代，有點像一個小巧的花瓶。希望渲染圖能體現出產品的質感，並暗示其智能化功能，例如可以加入一些虛擬的聲波或光效元素。', 8000, '2024-09-17 15:45:00', '2024-10-01 23:59:59', '2024-09-17 15:45:00', '徵件中', TRUE),
(6, '動漫角色立體紙雕', '紙雕藝術', '鬼滅之刃', '希望製作一個禰豆子的立體紙雕。作品高度大約30cm，要能體現出角色的特點，尤其是她的竹筒和粉色眼睛。希望整體感覺既可愛又帶有一絲神秘感。', 6000, '2024-09-18 09:30:00', '2024-10-02 18:00:00', '2024-09-18 09:30:00', '徵件中', FALSE),
(7, '糖果主題店鋪招牌', '商業設計', '無', '需要一個色彩繽紛的店鋪招牌設計。店名是「糖果雲朵」，希望能融入棉花糖、棒棒糖等元素。字體要活潑可愛，整體設計要讓人看了就想吃甜食！', 4500, '2024-09-19 14:00:00', '2024-09-26 23:59:59', '2024-09-19 14:00:00', '已成交', TRUE),
(8, '兒童繪本插畫', '插畫設計', '原創', '需要為我的新書「河馬哈利的大冒險」繪製12頁插畫。故事講述一隻害羞的小河馬如何克服恐懼，交到新朋友。畫風要溫馨可愛，色彩要明亮活潑。', 15000, '2024-09-20 10:45:00', '2024-10-20 18:00:00', '2024-09-20 10:45:00', '徵件中', FALSE),
(10, '音樂專輯封面設計', '平面設計', '大衛·鮑伊', '需要為我的搖滾專輯「星際迷航」設計封面。音樂風格融合了復古搖滾和未來電子音樂元素。希望封面能反映出這種時空交錯的感覺，可以考慮使用霓虹色彩和復古未來主義元素。', 5500, '2024-09-24 15:45:00', '2024-10-08 18:00:00', '2024-09-24 15:45:00', '已成交', FALSE),
(9, '氣候變化主題海報', '公益設計', '無', '需要一張強烈視覺衝擊的海報，主題是「氣候變化」。希望能通過某種創意方式展現出地球正面臨的危機，例如可以考慮使用對比手法。色調可以偏冷，營造出緊迫感。', 3500, '2024-09-21 16:20:00', '2024-10-05 23:59:59', '2024-09-21 16:20:00', '截止', TRUE);

-- 5-1-1 需求案件示意圖
INSERT INTO db_need_images (need_id, step, image_url) VALUES
(1, 1, '1_sketch1.png'),(1, 2, '1_sketch2.png'),(1, 3, '1_sketch3.png'),(1, 4, '1_sketch4.png'),(1, 5, '1_sketch5.png'),
(2, 1, '2_sketch1.png'),(2, 2, '2_sketch2.png'),(2, 3, '2_sketch3.png'),(2, 4, '2_sketch4.png'),(2, 5, '2_sketch5.png'),
(3, 1, '3_sketch1.png'),(3, 2, '3_sketch2.png'),(3, 3, '3_sketch3.png'),(3, 4, '3_sketch4.png'),(3, 5, '3_sketch5.png'),
(4, 1, '4_sketch1.png'),(4, 2, '4_sketch2.png'),(4, 3, '4_sketch3.png'),(4, 4, '4_sketch4.png'),(4, 5, '4_sketch5.png'),
(5, 1, '5_sketch1.png'),(5, 2, '5_sketch2.png'),(5, 3, '5_sketch3.png'),(5, 4, '5_sketch4.png'),(5, 5, '5_sketch5.png');

-- 5-2 接案假資料
INSERT INTO db_work_info (worker_id, work_title, work_category, work_original_from, work_description, work_price, usage_restrictions, tags, publish_time, deadline, last_update, work_status, public_status) VALUES
(6, '寵物客製化漫畫', '漫畫', '無', '將您的寵物製作成4格漫畫，可選擇日常有趣場景', 4500, '僅供個人使用，允許社交媒體分享', '寵物,萌,日常,療癒', '2024-01-12 13:25:00', '2024-02-12 23:59:59', '2024-01-30 11:40:00', '取消販售', false),
(10, '和風妖怪插畫', '插畫', '原創', '日式風格妖怪主題插畫，適合製作成掛軸或桌布', 7500, '允許非商業用途使用，需標註作者', '和風,妖怪,浮世繪,東方', '2024-01-16 12:40:00', '2024-02-16 23:59:59', '2024-01-29 16:15:00', '投稿審查', true),
(7, '虛擬主播形象設計', '角色設計', '原創', '可愛風格虛擬主播完整形象設計，含表情包和各角度展示', 20000, '商業用途需另議價格，需簽訂合約', 'Vtuber,可愛,表情包,動態', '2024-01-25 09:15:00', '2024-03-25 23:59:59', '2024-01-25 09:15:00', '公開販售', true),
(10, '量子蛋糕包裝設計', '食品包裝設計', '原創', '結合量子物理概念的蛋糕包裝，使用幾何圖形與粒子軌跡元素', 8500, '禁止修改設計，需標註設計師', '量子,幾何,未來感', '2024-10-04 09:00:00', '2024-11-04 23:59:59', '2024-10-04 09:00:00', '已成交', true),
(8, '刀劍神域同人立繪', '立繪', '刀劍神域', '亞絲娜婚紗版本立繪，內含5張差分，喜怒哀樂俱全', 6500, '禁止商用，允許個人使用和展示', '亞絲娜,婚紗,唯美,SAO', '2024-01-08 15:30:00', '2024-02-08 23:59:59', '2024-01-27 14:20:00', '已成交', true),
(9, '機甲設計圖', '機械設計', '原創', '科幻風格機甲設計，含武器系統和變形機制設計圖', 18000, '版權買斷需另議，基礎版本僅供參考', '機甲,科幻,機械,設計圖', '2024-01-22 11:50:00', '2024-03-22 23:59:59', '2024-01-22 11:50:00', '公開販售', true),
(10, '分子料理教學手冊插圖', '教育插畫', '無', '20組分子料理步驟分解插圖，需包含工具使用示意', 18000, '限教育用途，禁止轉售', '分子料理,教學,步驟圖', '2024-10-05 14:30:00', '2024-12-05 18:00:00', '2024-10-05 14:30:00', '公開販售', false),
(10, '科學實驗室主題LOGO', '品牌設計', '無', '融合燒杯、DNA鏈與顯微鏡元素的極簡風格LOGO', 12000, '商標註冊後方可商用', '科學,極簡,實驗室', '2024-10-06 11:15:00', '2024-10-20 23:59:59', '2024-10-06 11:15:00', '公開販售', true);

-- 5-2-1 作品原始檔
-- INSERT INTO db_work_original_file (work_id, original_file_url) VALUES
-- (8, 'document_preview_archive.ico'),(8, '統計數據202308中文版.pdf'),(8, '極簡風meme.zip');

-- 5-2-2 作品預覽圖
INSERT INTO db_work_images (work_id, step, image_url) VALUES
(1, 1, '1_sketch1.png'),(1, 2, '1_sketch2.png'),(1, 3, '1_sketch3.png'),(1, 4, '1_sketch4.png'),(1, 5, '1_sketch5.png'),
(2, 1, '2_sketch1.png'),(2, 2, '2_sketch2.png'),(2, 3, '2_sketch3.png'),(2, 4, '2_sketch4.png'),(2, 5, '2_sketch5.png'),
(3, 1, '3_sketch1.png'),(3, 2, '3_sketch2.png'),(3, 3, '3_sketch3.png'),(3, 4, '3_sketch4.png'),(3, 5, '3_sketch5.png'),
(4, 1, '4_sketch1.png'),(4, 2, '4_sketch2.png'),(4, 3, '4_sketch3.png'),(4, 4, '4_sketch4.png'),(4, 5, '4_sketch5.png'),
(5, 1, '5_sketch1.png'),(5, 2, '5_sketch2.png'),(5, 3, '5_sketch3.png'),(5, 4, '5_sketch4.png'),(5, 5, '5_sketch5.png'),
(6, 1, '6_sketch1.png'),(6, 2, '6_sketch2.png'),(6, 3, '6_sketch3.png'),(6, 4, '6_sketch4.png'),(6, 5, '6_sketch5.png'),
(7, 1, '7_sketch1.png'),(7, 2, '7_sketch2.png'),(7, 3, '7_sketch3.png'),(7, 4, '7_sketch4.png'),(7, 5, '7_sketch5.png');

-- 5-2-3 設定投稿至需求案
UPDATE db_work_info
SET case_by_need = '12'
WHERE work_id BETWEEN 1 AND 2;    

-- 5-3 公開名片表導入會員資料
-- INSERT INTO db_public_card_info (user_id, user_nickname, user_avatar, user_introduction)
-- SELECT 
--     user_id,
--     user_nickname,
--     NULL, -- 初始時用 NULL 填充 user_avatar
--     NULL -- 初始時用 NULL 填充 user_introduction
-- FROM member_basic;

INSERT INTO db_public_card_info (user_id, user_nickname, user_avatar, use_default_avatar, user_introduction, card_status, last_update) VALUES 
(1, '曲劍墨三馬', '1_avatar.png', true, '我是一名電商賣家，專注於販售時尚配飾。平時喜歡關注潮流趨勢，希望能為我的商品找到獨特的視覺呈現方式。', '公開', '2024-09-15 11:45:00'),
(2, '喜守間友仁', '2_avatar.png', false, '剛起步的遊戲實況主，希望透過有趣的視覺元素增加直播間的吸引力。對於設計完全是門外漢，但很願意嘗試新鮮的點子！', '公開', '2024-09-15 11:45:00'),
(3, '宮美春車', '3_avatar.png', false, '熱愛閱讀的大學生，正在籌備一個校園讀書會。希望通過有吸引力的視覺設計吸引更多同學參與。', '非公開', '2024-09-15 14:20:00'),
(4, '你行Nissan啊', '4_avatar.png', false, '退休教師，最近迷上了寫作，正在創作一本關於教育的回憶錄。希望能為書籍找到一個有意義的封面設計。', '公開', '2024-09-15 16:00:00'),
(5, '開封優格保七天', '5_avatar.png', true, '新創公司的創始人，專注於開發智能家居產品。希望通過吸引眼球的產品渲染圖來吸引潛在投資者的注意。', '非公開', '2024-09-16 09:15:00'),
(6, '潔西卡', '6_avatar.png', false, '動漫迷，喜歡cosplay。希望能將我最愛的角色變成獨特的藝術品。', '公開', '2024-09-16 11:30:00'),
(7, '跳跳糖味棉花糖', '7_avatar.png', false, '甜品店老闆，想為店鋪設計一個吸引眼球的招牌。', '公開', '2024-09-16 13:45:00'),
(8, '月光下的Hippo', '8_avatar.png', false, '兒童繪本作家，正在創作一本關於友誼的故事書。', '非公開', '2024-09-16 15:20:00'),
(9, '蘿莎' , '9_avatar.png', false, '環保組織成員，希望通過藝術喚起人們對氣候變化的關注。', '公開', '2024-09-16 17:00:00'),
(10, '電波系魔法少女', '10_avatar.png', false, '獨立遊戲開發者，正在製作一款魔法少女主題的手機遊戲。', '公開', '2024-09-17 09:30:00'),
(11, '', '', true, '', '未啟用', '2024-09-17 11:45:00');

UPDATE db_public_card_info -- 為 user_id 10 新增橫幅、喜好作品、屬性Tag、開啟價目表
SET 
    card_banner = '10_banner.png',
    use_default_banner = 0,
    involved_acgn = '進擊的巨人,SPY×FAMILY,鏈鋸人',
    key_tags = '腐向,奇幻風格,厚塗,日系畫風',
    sell_public_status = 1
WHERE 
    user_id = 10;

-- 5-3-1 公開名片價目表
INSERT INTO db_public_card_sell 
(user_id, sell_step, sell_title, sell_description, sell_price, sell_example_image_1, sell_example_image_2)
VALUES
(10, 1, '可愛風Q版頭像', '✨專長：可愛風格、動物、萌系人物
⭐工期：7-10個工作天
⭐修改次數：2次（大幅修改）
⭐急單加價：+50%（工期3-4天）
❌不接：獵奇、血腥題材', 
2500, 
'10_sell_1_1.png', 
'10_sell_1_2.png');

-- (10, 2, '精緻全身立繪', '✨專長：動漫風格、遊戲立繪、原創角色
-- ⭐工期：14-21個工作天
-- ⭐修改次數：3次（含草稿階段）
-- ⭐急單加價：+80%（工期7-10天）
-- ❌不接：成人向、暴力內容', 
-- 8500, 
-- '10_sell_2_1.png', 
-- '10_sell_2_2.png');
SET FOREIGN_KEY_CHECKS = 1;

--