-- 一、會員
-- 1-1 基本資料
CREATE TABLE member_basic (
    user_id INT AUTO_INCREMENT PRIMARY KEY,                 -- 用戶 ID，主鍵
    user_name VARCHAR(50) NOT NULL UNIQUE,                  -- 用戶名，唯一
    user_password VARCHAR(128) NULL,                    -- 用戶密碼
    user_phone VARCHAR(10) NULL UNIQUE,                 -- 手機號，唯一
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
login_id INT AUTO_INCREMENT PRIMARY KEY, 
user_id int not null,
provider ENUM('Line', 'Google', 'Facebook') NOT NULL,
google_user_id varchar(50) null unique,
line_user_id varchar(50) null unique,
fb_user_id varchar(50) null unique,
access_token varchar(128) null unique,
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
type_id INT AUTO_INCREMENT PRIMARY KEY,
user_id int not null,                            -- 關聯用戶ID
type_name varchar(50) null,                      -- 網站喜好類型
sort_order INT NOT NULL,                         -- 網站喜好順序
created_at timestamp default current_timestamp,  -- 記錄創建時間
updated_at timestamp default current_timestamp on update current_timestamp,  -- 記錄更新時間
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
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES member_basic (user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- 3-2 訂單基本資料(購買者資料、支付狀況、物流狀況...等)
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    recipient VARCHAR(100) NOT NULL,
    recipient_phone VARCHAR(15) NULL,
    city VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    detailed_address VARCHAR(255) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    coupon_code VARCHAR(50) DEFAULT NULL,
    coupon_discount DECIMAL(10, 2) DEFAULT NULL,
    order_status VARCHAR(15) NOT NULL DEFAULT 'PENDING',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES member_basic (user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



-- 3-2-1 金流資料
CREATE TABLE payment_transactions (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(9) NOT NULL,
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    payment_amount DECIMAL(10, 2) NOT NULL,
    transaction_id VARCHAR(100) DEFAULT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- 3-2-2 物流資料
CREATE TABLE shipping_details (
    shipping_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    shipping_status VARCHAR(10) NOT NULL,
    carrier_name VARCHAR(100) DEFAULT NULL,
    tracking_number VARCHAR(100) DEFAULT NULL,
    shipping_date DATETIME DEFAULT NULL,
    estimated_delivery_date DATE DEFAULT NULL,
    actual_delivery_date DATE DEFAULT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- 3-3 訂單的商品項目資料
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    product_price DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    UNIQUE (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


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
    coupon_code VARCHAR(50) UNIQUE NOT NULL,
    discount_type VARCHAR(10) NOT NULL,
    discount_value DECIMAL(10, 2) NOT NULL,
    min_purchase DECIMAL(10, 2) DEFAULT NULL,
    max_discount DECIMAL(10, 2) DEFAULT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4-3 紀錄會員領取的優惠券
CREATE TABLE Usercoupons (
    user_coupon_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    coupon_id INT NOT NULL,
    usage_limit INT DEFAULT NULL,  -- 此會員的使用次數限制
    usage_count INT DEFAULT 0,     -- 此會員已使用次數
    used_in_order_id INT DEFAULT NULL,
    used_at DATETIME DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES member_basic(user_id) ON DELETE CASCADE,
    FOREIGN KEY (coupon_id) REFERENCES coupons(coupon_id) ON DELETE CASCADE,
    FOREIGN KEY (used_in_order_id) REFERENCES orders(order_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 五、委託
-- 5-1 需求資訊表
SET FOREIGN_KEY_CHECKS = 0;
CREATE TABLE db_need_info (
    needer_id INT NOT NULL,                         -- 需求人id（關聯資料表：使用者資訊表member_basic)
    -- 嘗試拔掉讓它直接去db_public_card_info找資料
    -- needer_nickname VARCHAR(50),                    -- 需求人暱稱（關聯資料表：公開名片表db_public_card_info)
    -- needer_avatar VARCHAR(255),                     -- 需求人大頭（關聯資料表：公開名片表db_public_card_info)    
    -- needer_introduction VARCHAR(300),               -- 需求人介紹（關聯資料表：公開名片表db_public_card_info)

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
    public_status BOOLEAN DEFAULT TRUE,             -- 是否於名片頁公開
    case_by_work INT,                               -- 配對投稿作品id

    reviewer_id INT,                                -- 評價人id（關聯資料表：使用者資訊表member_basic)
    reviewer_nickname VARCHAR(50),                  -- 評價人暱稱（關聯資料表：公開名片表db_public_card_info)
    reviewer_avatar VARCHAR(255),                   -- 評價人頭像（關聯資料表：公開名片表db_public_card_info)
    reviewer_star INT,                              -- 評價星等
    review_content TEXT,                            -- 評價人評價內容
    review_time DATETIME,                           -- 評價時間
    review_status VARCHAR(10),                      -- 評價狀態（未評價、已評價、尚未開放）

    FOREIGN KEY (needer_id) REFERENCES member_basic(user_id) ON DELETE RESTRICT, -- 外鍵 需求人id → member_basic使用者資訊表-使用者id
    -- 嘗試拔掉讓它直接去db_public_card_info找資料
    -- FOREIGN KEY (needer_nickname) REFERENCES db_public_card_info(user_nickname) ON DELETE SET NULL, -- 外鍵 需求人暱稱 → 公開名片表-使用者暱稱
    -- FOREIGN KEY (needer_avatar) REFERENCES db_public_card_info(user_avatar) ON DELETE SET NULL, -- 外鍵 需求人大頭 → 公開名片表-使用者大頭
    -- FOREIGN KEY (needer_introduction) REFERENCES db_public_card_info(user_introduction) ON DELETE SET NULL, -- 外鍵 需求人介紹 → 公開名片表-使用者介紹
        
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
CREATE TABLE db_work_info (
    worker_id INT NOT NULL,                         -- 作者id（關聯資料表：使用者資訊表member_basic）
    -- 嘗試拔掉讓它直接去db_public_card_info找資料
    -- author_nickname VARCHAR(50),                    -- 作者暱稱（關聯資料表：公開名片表db_public_card_info）
    -- author_avatar VARCHAR(255),                     -- 作者大頭（關聯資料表：公開名片表db_public_card_info）
    -- author_introduction VARCHAR(300),               -- 作者介紹（關聯資料表：公開名片表db_public_card_info）

    work_id INT AUTO_INCREMENT PRIMARY KEY,         -- 作品id
    work_title VARCHAR(50),                         -- 作品標題
    work_category VARCHAR(50),                      -- 販賣項目
    work_original_from VARCHAR(150),                -- 作品關聯原作
    work_description TEXT,                          -- 作品說明
    work_price DECIMAL(10),                         -- 作品售價
    usage_restrictions TEXT,                        -- 使用限制
    tags VARCHAR(100),                              -- Tag
    original_file BOOLEAN DEFAULT FALSE,            -- 原始檔解鎖
    publish_time DATETIME,                          -- 發布時間
    deadline DATETIME,                              -- 截止時間
    last_update DATETIME,                           -- 最後更新
    work_status VARCHAR(10),                        -- 作品狀態
    public_status BOOLEAN DEFAULT TRUE,             -- 是否於名片頁公開
    case_by_need INT,                               -- 投稿需求案id

    reviewer_id INT,                                -- 評價人id（關聯資料表：使用者資訊表member_basic）
    reviewer_nickname VARCHAR(50),                  -- 評價人暱稱（關聯資料表：公開名片表db_public_card_info）
    reviewer_avatar VARCHAR(255),                   -- 評價人頭像（關聯資料表：公開名片表db_public_card_info）
    reviewer_star INT,                              -- 評價星等
    review_content TEXT,                            -- 評價人評價內容
    review_time DATETIME,                           -- 評價時間
    review_status VARCHAR(10),                      -- 評價狀態（未評價、已評價、尚未開放）
    
    FOREIGN KEY (worker_id) REFERENCES member_basic(user_id) ON DELETE RESTRICT, -- 外鍵 作者id → member_basic使用者資訊表-使用者id
    -- 嘗試拔掉讓它直接去db_public_card_info找資料
    -- FOREIGN KEY (author_nickname) REFERENCES db_public_card_info(user_nickname) ON DELETE SET NULL, -- 外鍵 作者暱稱 → 公開名片表-使用者暱稱
    -- FOREIGN KEY (author_avatar) REFERENCES db_public_card_info(user_avatar) ON DELETE SET NULL, -- 外鍵 作者大頭 → 公開名片表-使用者大頭
    -- FOREIGN KEY (author_introduction) REFERENCES db_public_card_info(user_introduction) ON DELETE SET NULL, -- 外鍵 作者介紹 → 公開名片表-使用者介紹

    INDEX idx_work_title (work_title),
    INDEX idx_work_original_from (work_original_from),
    INDEX idx_work_price (work_price)
);

-- 5-2-1 作品原始檔
CREATE TABLE db_work_original_file (
    original_file_id INT AUTO_INCREMENT PRIMARY KEY,-- 原始檔上傳流水號
    work_id INT,                                    -- 作品id
    -- step INT,                                        第幾個檔
    original_file_url VARCHAR(255),                 -- 原始檔名
    FOREIGN KEY (work_id) REFERENCES db_work_info(work_id) ON DELETE CASCADE
);

-- 5-2-2 作品預覽圖
CREATE TABLE db_work_images (
    image_id INT AUTO_INCREMENT PRIMARY KEY,      -- 預覽圖上傳流水號
    work_id INT,                                    -- 作品id
    step INT,                                       -- 第幾張圖
    image_url VARCHAR(255),                       -- 圖檔名
    FOREIGN KEY (work_id) REFERENCES db_work_info(work_id) ON DELETE CASCADE
);

-- 5-3 公開名片表
CREATE TABLE db_public_card_info (
    user_id INT NOT NULL PRIMARY KEY,                 -- 使用者id（關聯資料表：使用者資訊表member_basic）
    user_nickname VARCHAR(50) NOT NULL,               -- 使用者暱稱（關聯資料表：需求need_info、作品work_info）
    user_avatar VARCHAR(255) DEFAULT NULL,            -- 使用者頭像（關聯資料表：需求need_info、作品work_info）
    use_default_avatar BOOLEAN DEFAULT TRUE,          -- 是否使用預設頭像
    user_introduction VARCHAR(300) DEFAULT NULL,      -- 使用者介紹（關聯資料表：需求need_info、作品work_info）
    card_banner VARCHAR(255),                         -- 名片橫幅
    use_default_banner BOOLEAN DEFAULT TRUE,          -- 是否使用預設橫幅
    card_status VARCHAR(3) DEFAULT '非公開',          -- 名片公開狀態
    involved_acgn TEXT,                              -- 涉獵作品
    key_tags VARCHAR(255),                            -- 關鍵Tag

    work_id INT,                                      -- 公開/已成交作品id（關聯資料表：作品work_info）
    work_title VARCHAR(50),                           -- 作品標題（關聯資料表：作品work_info）
    work_original_from VARCHAR(150),                  -- 作品關聯原作（關聯資料表：作品work_info）
    work_price DECIMAL(10),                           -- 作品售價（關聯資料表：作品work_info）
    need_id INT,                                      -- 發起需求id（關聯資料表：需求need_info）
    -- 嘗試拔掉讓它直接去db_need_info找資料
    -- need_title VARCHAR(50),                           -- 發起需求標題（關聯資料表：需求need_info）
    -- need_original_from VARCHAR(150),                  -- 需求關聯原作（關聯資料表：需求need_info）
    -- need_price DECIMAL(10),                           -- 酬金（關聯資料表：需求need_info）
    deal_count INT,                                   -- 成交計數
    sell_public_status BOOLEAN DEFAULT FALSE,          -- 價目表 是否公開開關
    work_sellnow_list_public_status BOOLEAN DEFAULT TRUE,     -- 公開作品列表 是否公開開關
    work_done_list_public_status BOOLEAN DEFAULT TRUE,-- 已成交作品列表 是否公開開關
    need_list_public_status BOOLEAN DEFAULT TRUE,     -- 發起需求列表 是否公開開關
    last_update DATETIME,                             -- 最後更新
    
    FOREIGN KEY (user_id) REFERENCES member_basic(user_id) ON DELETE RESTRICT, -- 外鍵 使用者id → member_basic使用者資訊表-使用者id
    FOREIGN KEY (work_id) REFERENCES db_work_info(work_id) ON DELETE SET NULL, -- 外鍵 公開/已成交作品id → 作品資訊表-作品id
    FOREIGN KEY (work_title) REFERENCES db_work_info(work_title) ON DELETE SET NULL, -- 外鍵 作品標題 → 作品資訊表-作品標題
    FOREIGN KEY (work_original_from) REFERENCES db_work_info(work_original_from) ON DELETE SET NULL, -- 外鍵 作品關聯原作 → 作品資訊表-作品關聯原作
    FOREIGN KEY (work_price) REFERENCES db_work_info(work_price) ON DELETE SET NULL, -- 外鍵 作品售價 → 作品資訊表-作品售價
    FOREIGN KEY (need_id) REFERENCES db_need_info(need_id) ON DELETE SET NULL, -- 外鍵 發起需求id → 需求資訊表-需求案id
    -- FOREIGN KEY (need_title) REFERENCES db_need_info(need_title) ON DELETE SET NULL, -- 外鍵 發起需求標題 → 需求資訊表-需求標題
    -- FOREIGN KEY (need_original_from) REFERENCES db_need_info(need_original_from) ON DELETE SET NULL, -- 外鍵 需求關聯原作 → 需求資訊表-需求關聯原作
    -- FOREIGN KEY (need_price) REFERENCES db_need_info(need_price) ON DELETE SET NULL, -- 外鍵 酬金 → 需求資訊表-酬金

    INDEX idx_user_nickname (user_nickname),
    INDEX idx_user_avatar (user_avatar),
    INDEX idx_user_introduction (user_introduction)
);

-- 5-3-1 公開價目表
CREATE TABLE db_public_card_sell (
    sell_list_id INT AUTO_INCREMENT PRIMARY KEY,      -- 項目流水號
    user_id INT,                                      -- 使用者id
    sell_step INT,                                    -- 項目排序
    sell_title TEXT,                                  -- 販售項目
    sell_description TEXT,                            -- 販售說明
    sell_price INT,                                   -- 售價
    sell_example_image_1 VARCHAR(255),                -- 範例圖1
    sell_example_image_2 VARCHAR(255),                -- 範例圖2
    FOREIGN KEY (user_id) REFERENCES db_public_card_info(user_id) ON DELETE CASCADE
);
SET FOREIGN_KEY_CHECKS = 1;
