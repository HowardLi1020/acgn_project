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


