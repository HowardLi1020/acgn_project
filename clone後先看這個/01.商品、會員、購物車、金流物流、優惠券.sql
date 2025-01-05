-- 一、會員
-- 1-1 基本資料
CREATE TABLE member_basic (
    user_id INT AUTO_INCREMENT PRIMARY KEY,                 -- 用戶 ID，主鍵
    user_name VARCHAR(20) NOT NULL UNIQUE,                  -- 用戶名，唯一
    user_password VARCHAR(128) NOT NULL,                    -- 用戶密碼
    user_phone VARCHAR(10) NOT NULL UNIQUE,                 -- 手機號，唯一
    user_email VARCHAR(120) NOT NULL UNIQUE,                -- 電子郵件，唯一
    user_nickname VARCHAR(20) NULL,                         -- 用戶暱稱
    user_gender ENUM('male', 'female', 'prefer_not_to_say') DEFAULT 'prefer_not_to_say', -- 性別
    user_birth DATE NULL,                                   -- 出生日期
    user_address TEXT NULL,                                 -- 地址
    vip_status TINYINT(1) DEFAULT 0,                        -- VIP 狀態
    user_avatar VARCHAR(255) DEFAULT 'default.png',         -- 用戶頭像
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,         -- 創建時間
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 更新時間
    INDEX idx_user_email_phone (user_email, user_phone)     -- 複合索引
);

-- 1-1-1 會員登入表
create table member_login(
login_id int primary key,
user_id int not null,
provider varchar(50) null,
provider_id_google varchar(50) null unique,
provider_id_line varchar(50) null unique,
provider_id_fb varchar(50) null unique,
access_token varchar(50) null unique,
created_at timestamp default current_timestamp,
updated_at timestamp default current_timestamp on update current_timestamp,
foreign key (user_id) references member_basic(user_id) ON DELETE CASCADE
);

-- 1-2 會員頭像
CREATE TABLE member_photos (
    photo_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,                     -- 關聯用戶ID
    photo_url VARCHAR(255) NOT NULL,          -- 照片存儲的URL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp default current_timestamp on update current_timestamp,
    FOREIGN KEY (user_id) REFERENCES member_basic(user_id) ON DELETE CASCADE
);

-- 1-3 隱私設置
CREATE TABLE member_privacy (
    privacy_id INT AUTO_INCREMENT PRIMARY KEY,         -- 隱私設置的唯一標識
    user_id INT NOT NULL,                              -- 關聯用戶ID
    phone_verified BOOLEAN DEFAULT FALSE,             -- 手機驗證狀態
    email_verified BOOLEAN DEFAULT FALSE,             -- 郵箱驗證狀態
    account_verify BOOLEAN DEFAULT FALSE,             -- 帳號是否啟用
    activity_checked BOOLEAN DEFAULT FALSE,           -- 是否啟用帳戶活動檢查
    double_verify BOOLEAN DEFAULT FALSE,              -- 是否啟用雙重驗證
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 記錄創建時間
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 記錄更新時間
    FOREIGN KEY (user_id) REFERENCES member_basic(user_id) ON DELETE CASCADE
);

-- 1-4 首頁類型設定
create table member_indextype(
type_id int primary key,
user_id int not null,
type_name varchar(50) null,
created_at timestamp default current_timestamp,
updated_at timestamp default current_timestamp on update current_timestamp,
foreign key (user_id) references member_basic(user_id) ON DELETE CASCADE
);

-- 1-5 身分驗證
CREATE TABLE member_verify (
    verify_id INT AUTO_INCREMENT PRIMARY KEY,         -- 唯一驗證記錄標識
    user_id INT NOT NULL,                             -- 關聯用戶ID
    change_value VARCHAR(255) DEFAULT NULL,           -- 提交變更的手機號或郵箱或密碼
    verification_code VARCHAR(6) NOT NULL,            -- 驗證碼（6位數）
    verification_token VARCHAR(64) DEFAULT NULL,      -- 驗證令牌（可用於更高安全級別的驗證）
    verification_type ENUM('registration', 'two_factor', 'password_change', 'phone_change', 'email_change') NOT NULL, -- 驗證類型
    code_used BOOLEAN DEFAULT FALSE,                  -- 驗證碼是否已使用
    token_used BOOLEAN DEFAULT FALSE,                 -- 驗證令牌是否已使用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- 驗證碼生成時間
    expires_at TIMESTAMP DEFAULT NULL,                -- 驗證碼過期時間
    FOREIGN KEY (user_id) REFERENCES member_basic(user_id) ON DELETE CASCADE
);

-- 1-6 後台管理者
create table auth_user(
superuser_id int primary key auto_increment,
superuser_name varchar(50) not null unique,
superuser_email varchar(120) not null unique,
superuser_password varchar(128) not null,
created_at timestamp default current_timestamp,
updated_at timestamp default current_timestamp on update current_timestamp
);

-- 二、商品
-- 2-1 品牌
CREATE TABLE product_brands (
    brand_id INT AUTO_INCREMENT PRIMARY KEY,
    brand_name VARCHAR(255) NOT NULL UNIQUE,  -- 品牌名稱
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2-2 系列
CREATE TABLE product_series (
    series_id INT AUTO_INCREMENT PRIMARY KEY,
    series_name VARCHAR(255) NOT NULL UNIQUE,  -- 系列名稱
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2-3 類別
CREATE TABLE product_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL UNIQUE,  -- 類別名稱
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2-4 商品信息
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,         -- 商品名稱
    description_text TEXT,                      -- 商品描述
    user_id INT,                                -- 添加用户ID
    brand_id INT,                               -- 品牌ID
    series_id INT,                              -- 系列ID
    category_id INT,                            -- 類別ID
    price DECIMAL(10, 2) NOT NULL,              -- 商品價格
    stock INT NOT NULL CHECK (stock >= 0),      -- 庫存數量
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES member_basic(user_id) ON DELETE CASCADE,
    FOREIGN KEY (brand_id) REFERENCES product_brands(brand_id) ON DELETE SET NULL,
    FOREIGN KEY (series_id) REFERENCES product_series(series_id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES product_categories(category_id) ON DELETE SET NULL
);

-- 2-5 商品圖片
CREATE TABLE product_images (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,                    -- 商品ID
    image_url VARCHAR(255) NOT NULL,            -- 圖片URL
    is_main BOOLEAN DEFAULT FALSE,              -- 是否為主圖片
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- 2-6 商品評價
CREATE TABLE product_reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,                    -- 商品ID
    user_id INT NOT NULL,                       -- 用戶ID
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),  -- 評分（1到5）
    review_text TEXT,                           -- 評價文字
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES member_basic(user_id) ON DELETE CASCADE
);

-- 2-7 商品收藏
CREATE TABLE product_wishlist (
    wishlist_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,                       -- 用戶ID
    product_id INT NOT NULL,                    -- 商品ID
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES member_basic(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- 2-8 商品留言
CREATE TABLE product_comments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,                    -- 商品ID
    user_id INT NOT NULL,                       -- 用戶ID
    content TEXT NOT NULL,                      -- 留言內容
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES member_basic(user_id) ON DELETE CASCADE
);

-- 2-9 商品推薦
CREATE TABLE product_recommendations (
    recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,                       -- 用戶ID
    product_id INT NOT NULL,                    -- 當前商品ID
    recommended_product_id INT NOT NULL,        -- 推薦的商品ID
    recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES member_basic(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (recommended_product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- 三、購物車
-- 3-1 購物車項目
CREATE TABLE shopping_cart_items (
    cart_item_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,                          -- 關聯用戶ID
    product_id INT NOT NULL,                         -- 關聯商品ID
    quantity INT NOT NULL CHECK (quantity > 0),      -- 商品數量
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 添加時間
    FOREIGN KEY (member_id) REFERENCES member_basic(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- 3-2 訂單基本資料(購買者資料、支付狀況、物流狀況...等)
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,                              -- 關聯用戶ID
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- 訂單生成時間
    recipient VARCHAR(100) NOT NULL,                    -- 收件人姓名
    city VARCHAR(100) NOT NULL,                         -- 城市
    region VARCHAR(100) NOT NULL,                       -- 地區
    detailed_address VARCHAR(255) NOT NULL,             -- 詳細地址
    postal_code VARCHAR(20) NOT NULL,                   -- 郵遞區號
    total_amount DECIMAL(10, 2) NOT NULL,               -- 訂單總金額
    coupon_code VARCHAR(50) DEFAULT NULL,               -- 使用的優惠券代碼
    coupon_discount DECIMAL(10, 2) DEFAULT 0.00,        -- 優惠券折扣金額
    payment_status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending', -- 支付狀態
    shipping_status ENUM('pending', 'shipped', 'in_transit', 'delivered', 'returned', 'canceled') DEFAULT 'pending', -- 配送狀態
    payment_method ENUM('credit_card', 'paypal', 'cash_on_delivery') NOT NULL,  -- 支付方式
    order_status ENUM('pending', 'shipped', 'delivered', 'canceled') NOT NULL,  -- 訂單狀態
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,       -- 訂單建立時間
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 訂單更新時間
    FOREIGN KEY (member_id) REFERENCES member_basic(user_id) ON DELETE CASCADE
);


-- 3-2-1 金流資料
CREATE TABLE payment_transactions (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,                              -- 關聯訂單ID
    payment_method ENUM('credit_card', 'paypal', 'cash_on_delivery') NOT NULL,  -- 支付方式
    payment_status ENUM('pending', 'completed', 'failed', 'refunded') NOT NULL, -- 支付狀態
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- 支付時間
    payment_amount DECIMAL(10, 2) NOT NULL,             -- 支付金額
    transaction_id VARCHAR(100) DEFAULT NULL,           -- 第三方支付流水號
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- 3-2-2 物流資料
CREATE TABLE shipping_details (
    shipping_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,                              -- 關聯訂單ID
    shipping_status ENUM('pending', 'shipped', 'in_transit', 'delivered', 'returned', 'canceled') NOT NULL, -- 配送狀態
    carrier_name VARCHAR(100) DEFAULT NULL,             -- 承運商名稱
    tracking_number VARCHAR(100) DEFAULT NULL,          -- 物流追蹤編號
    shipping_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 出貨時間
    estimated_delivery_date DATE DEFAULT NULL,          -- 預計送達時間
    actual_delivery_date DATE DEFAULT NULL,             -- 實際送達時間
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- 3-3 訂單的商品項目資料
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,                          -- 關聯訂單ID
    product_id INT NOT NULL,                        -- 商品ID
    product_price DECIMAL(10, 2) NOT NULL,          -- 商品價格
    quantity INT NOT NULL CHECK (quantity > 0),     -- 商品數量
    subtotal DECIMAL(10, 2) GENERATED ALWAYS AS (product_price * quantity) STORED, -- 小計
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- 3-4 用戶對訂單的評分(交易評價、買賣家評價...等)
CREATE TABLE product_member_ratings (
    rating_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,                          -- 評分用戶ID
    rated_by_user_id INT NOT NULL,                 -- 被評分用戶ID
    order_id INT NOT NULL,                         -- 關聯訂單ID
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),  -- 評分（1到5）
    rating_type ENUM('buyer', 'seller') NOT NULL,  -- 評分類型（買家或賣家）
    rating_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 評分日期
    FOREIGN KEY (user_id) REFERENCES member_basic(user_id) ON DELETE CASCADE,
    FOREIGN KEY (rated_by_user_id) REFERENCES member_basic(user_id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- 四、優惠券
-- 4-1 優惠券基本資料
CREATE TABLE Coupons (
    coupon_id INT AUTO_INCREMENT PRIMARY KEY,
    coupon_code VARCHAR(50) NOT NULL UNIQUE,         -- 優惠券代碼
    discount_type ENUM('amount', 'percentage') NOT NULL, -- 折扣類型：金額折扣或百分比折扣
    discount_value DECIMAL(10, 2) NOT NULL,          -- 折扣值：金額或百分比
    min_purchase DECIMAL(10, 2) DEFAULT 0.00,        -- 最低消費金額，0表示無限制
    max_discount DECIMAL(10, 2) DEFAULT NULL,        -- 最大折扣金額（百分比折扣適用）
    start_date DATE NOT NULL,                        -- 優惠券開始日期
    end_date DATE NOT NULL,                          -- 優惠券結束日期
    usage_limit INT DEFAULT NULL,                    -- 優惠券總使用次數限制
    used_count INT DEFAULT 0,                        -- 優惠券已使用次數
    is_active BOOLEAN DEFAULT TRUE,                  -- 是否啟用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 4-3 紀錄會員領取的優惠券
CREATE TABLE UserCoupons (
    user_coupon_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,                            -- 使用者ID
    coupon_id INT NOT NULL,                          -- 關聯優惠券ID
    is_used BOOLEAN DEFAULT FALSE,                   -- 是否已使用
    used_in_order_id INT DEFAULT NULL,               -- 使用的訂單ID
    used_at TIMESTAMP NULL,                          -- 使用日期
    FOREIGN KEY (user_id) REFERENCES member_basic(user_id) ON DELETE CASCADE,
    FOREIGN KEY (coupon_id) REFERENCES Coupons(coupon_id) ON DELETE CASCADE,
    FOREIGN KEY (used_in_order_id) REFERENCES orders(order_id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 五、委託
-- 5-1 需求資訊表
SET FOREIGN_KEY_CHECKS = 0;
CREATE TABLE db_need_info (
    needer_id INT NOT NULL,                         -- 需求人id（關聯資料表：使用者資訊表member_basic)
    needer_nickname VARCHAR(50),                    -- 需求人暱稱（關聯資料表：公開名片表db_public_card_info)
    needer_avatar VARCHAR(255),                     -- 需求人大頭（關聯資料表：公開名片表db_public_card_info)    
    needer_introduction VARCHAR(300),               -- 需求人介紹（關聯資料表：公開名片表db_public_card_info)
    need_id INT AUTO_INCREMENT PRIMARY KEY,         -- 需求案id
    need_title VARCHAR(50),                         -- 需求標題
    need_category VARCHAR(50),                      -- 需求種類
    need_original_from VARCHAR(150),                -- 需求關聯原作
    need_description TEXT,                          -- 需求說明
    need_price DECIMAL(10),                         -- 酬金
    publish_time DATETIME,                          -- 發布時間
    deadline DATETIME,                              -- 截止時間
    last_update DATETIME,                           -- 最後更新
    need_status VARCHAR(10),                        -- 需求狀態
    
    reviewer_id INT,                                -- 評價人id（關聯資料表：使用者資訊表member_basic)
    reviewer_nickname VARCHAR(50),                  -- 評價人暱稱（關聯資料表：公開名片表db_public_card_info)
    reviewer_avatar VARCHAR(255),                   -- 評價人頭像（關聯資料表：公開名片表db_public_card_info)
    reviewer_star INT,                              -- 評價星等
    review_content TEXT,                            -- 評價人評價內容
    review_time DATETIME,                           -- 評價時間
    review_status VARCHAR(10),                      -- 評價狀態（未評價、已評價、尚未開放）

    FOREIGN KEY (needer_id) REFERENCES member_basic(user_id) ON DELETE RESTRICT, -- 外鍵 需求人id → member_basic使用者資訊表-使用者id
    FOREIGN KEY (needer_nickname) REFERENCES db_public_card_info(user_nickname) ON DELETE SET NULL, -- 外鍵 需求人暱稱 → 公開名片表-使用者暱稱
    FOREIGN KEY (needer_avatar) REFERENCES db_public_card_info(user_avatar) ON DELETE SET NULL, -- 外鍵 需求人大頭 → 公開名片表-使用者大頭
    FOREIGN KEY (needer_introduction) REFERENCES db_public_card_info(user_introduction) ON DELETE SET NULL, -- 外鍵 需求人介紹 → 公開名片表-使用者介紹
        
    INDEX idx_need_title (need_title),
    INDEX idx_need_original_from (need_original_from),
    INDEX idx_need_price (need_price)
);

-- 5-1-1 需求示意圖表
CREATE TABLE db_need_images (
    image_id INT AUTO_INCREMENT PRIMARY KEY,        -- 圖片上傳流水號
    need_id INT,                                    -- 需求案id
    step INT,                                       -- 第幾張圖
    image_url VARCHAR(255),                         -- 圖檔名
    FOREIGN KEY (need_id) REFERENCES db_need_info(need_id) ON DELETE CASCADE
);

-- 5-2 作品資訊表
CREATE TABLE db_works_info (
    author_id INT NOT NULL,                         -- 作者id（關聯資料表：使用者資訊表member_basic）
    author_nickname VARCHAR(50),                    -- 作者暱稱（關聯資料表：公開名片表db_public_card_info）
    author_avatar VARCHAR(255),                     -- 作者大頭（關聯資料表：公開名片表db_public_card_info）
    author_introduction VARCHAR(300),               -- 作者介紹（關聯資料表：公開名片表db_public_card_info）
    work_id INT AUTO_INCREMENT PRIMARY KEY,         -- 作品id
    work_title VARCHAR(50),                         -- 作品標題
    work_original_from VARCHAR(150),                -- 作品關聯原作
    work_description TEXT,                          -- 作品說明
    usage_restrictions TEXT,                        -- 使用限制
    sale_items TEXT,                                -- 販賣項目
    tags VARCHAR(100),                              -- Tag
    work_price DECIMAL(10),                         -- 作品售價
    original_file VARCHAR(255),                     -- 作品原始檔上傳
    submission_history TEXT,                         -- 投稿歷史
    work_thumbnail VARCHAR(255),                     -- 作品縮圖
    publish_time DATETIME,                          -- 發布時間
    deadline DATETIME,                              -- 截止時間
    last_update DATETIME,                           -- 最後更新
    work_status VARCHAR(10),                        -- 作品狀態

    reviewer_id INT,                                -- 評價人id（關聯資料表：使用者資訊表member_basic）
    reviewer_nickname VARCHAR(50),                  -- 評價人暱稱（關聯資料表：公開名片表db_public_card_info）
    reviewer_avatar VARCHAR(255),                   -- 評價人頭像（關聯資料表：公開名片表db_public_card_info）
    reviewer_star INT,                              -- 評價星等
    review_content TEXT,                            -- 評價人評價內容
    review_time DATETIME,                           -- 評價時間
    review_status VARCHAR(10),                      -- 評價狀態（未評價、已評價、尚未開放）
    
    FOREIGN KEY (author_id) REFERENCES member_basic(user_id) ON DELETE RESTRICT, -- 外鍵 作者id → member_basic使用者資訊表-使用者id
    FOREIGN KEY (author_nickname) REFERENCES db_public_card_info(user_nickname) ON DELETE SET NULL, -- 外鍵 作者暱稱 → 公開名片表-使用者暱稱
    FOREIGN KEY (author_avatar) REFERENCES db_public_card_info(user_avatar) ON DELETE SET NULL, -- 外鍵 作者大頭 → 公開名片表-使用者大頭
    FOREIGN KEY (author_introduction) REFERENCES db_public_card_info(user_introduction) ON DELETE SET NULL, -- 外鍵 作者介紹 → 公開名片表-使用者介紹

    INDEX idx_work_title (work_title),
    INDEX idx_work_original_from (work_original_from),
    INDEX idx_work_price (work_price)
);

-- 5-2-1 作品預覽圖
CREATE TABLE db_works_preview (
    preview_id INT AUTO_INCREMENT PRIMARY KEY,      -- 預覽圖上傳流水號
    work_id INT,                                    -- 作品id
    step INT,                                       -- 第幾張圖
    preview_url VARCHAR(255),                       -- 圖檔名
    FOREIGN KEY (work_id) REFERENCES db_works_info(work_id) ON DELETE CASCADE
);

-- 5-3 公開名片表
CREATE TABLE db_public_card_info (
    user_id INT NOT NULL PRIMARY KEY,                 -- 使用者id（關聯資料表：使用者資訊表member_basic）
    user_nickname VARCHAR(50) NOT NULL,               -- 使用者暱稱（關聯資料表：需求need_info、作品works_info）
    user_avatar VARCHAR(255) NOT NULL,                -- 使用者大頭（關聯資料表：需求need_info、作品works_info）
    user_introduction VARCHAR(300) NULL DEFAULT NULL, -- 使用者介紹（關聯資料表：需求need_info、作品works_info）
    card_banner VARCHAR(255),                         -- 名片橫幅
    card_status VARCHAR(3) DEFAULT '非公開',          -- 名片公開狀態
    involved_works TEXT,                              -- 涉獵作品
    key_tags VARCHAR(255),                            -- 關鍵Tag

    work_id INT,                                      -- 公開/已成交作品id（關聯資料表：作品works_info）
    work_title VARCHAR(50),                           -- 作品標題（關聯資料表：作品works_info）
    work_original_from VARCHAR(150),                  -- 作品關聯原作（關聯資料表：作品works_info）
    work_price DECIMAL(10),                           -- 作品售價（關聯資料表：作品works_info）
    need_id INT,                                      -- 發起需求id（關聯資料表：需求need_info）
    need_title VARCHAR(50),                           -- 發起需求標題（關聯資料表：需求need_info）
    need_original_from VARCHAR(150),                  -- 需求關聯原作（關聯資料表：需求need_info）
    need_price DECIMAL(10),                           -- 酬金（關聯資料表：需求need_info）
    deal_count INT,                                   -- 成交計數
    last_update DATETIME,                             -- 最後更新
    
    FOREIGN KEY (user_id) REFERENCES member_basic(user_id) ON DELETE RESTRICT, -- 外鍵 使用者id → member_basic使用者資訊表-使用者id
    FOREIGN KEY (work_id) REFERENCES db_works_info(work_id) ON DELETE SET NULL, -- 外鍵 公開/已成交作品id → 作品資訊表-作品id
    FOREIGN KEY (work_title) REFERENCES db_works_info(work_title) ON DELETE SET NULL, -- 外鍵 作品標題 → 作品資訊表-作品標題
    FOREIGN KEY (work_original_from) REFERENCES db_works_info(work_original_from) ON DELETE SET NULL, -- 外鍵 作品關聯原作 → 作品資訊表-作品關聯原作
    FOREIGN KEY (work_price) REFERENCES db_works_info(work_price) ON DELETE SET NULL, -- 外鍵 作品售價 → 作品資訊表-作品售價
    FOREIGN KEY (need_id) REFERENCES db_need_info(need_id) ON DELETE SET NULL, -- 外鍵 發起需求id → 需求資訊表-需求案id
    FOREIGN KEY (need_title) REFERENCES db_need_info(need_title) ON DELETE SET NULL, -- 外鍵 發起需求標題 → 需求資訊表-需求標題
    FOREIGN KEY (need_original_from) REFERENCES db_need_info(need_original_from) ON DELETE SET NULL, -- 外鍵 需求關聯原作 → 需求資訊表-需求關聯原作
    FOREIGN KEY (need_price) REFERENCES db_need_info(need_price) ON DELETE SET NULL, -- 外鍵 酬金 → 需求資訊表-酬金

    INDEX idx_user_nickname (user_nickname),
    INDEX idx_user_avatar (user_avatar),
    INDEX idx_user_introduction (user_introduction)
);

-- 5-3-1 公開價目表
CREATE TABLE db_public_card_sell (
    sell_list_id INT AUTO_INCREMENT PRIMARY KEY,      -- 項目流水號
    user_id INT,                                      -- 使用者id
    sell_title TEXT,                                  -- 販售項目
    sell_description TEXT,                            -- 販售說明
    sell_price INT,                                   -- 售價
    sell_example_image VARCHAR(255),                  -- 範例圖
    FOREIGN KEY (user_id) REFERENCES db_public_card_info(user_id) ON DELETE CASCADE
);
SET FOREIGN_KEY_CHECKS = 1;
