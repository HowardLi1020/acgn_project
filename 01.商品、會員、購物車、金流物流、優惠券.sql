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

-- 1-4 首頁類型設定
create table member_indextype(
type_id int primary key,
user_id int not null,
type_name varchar(50) null,
created_at timestamp default current_timestamp,
updated_at timestamp default current_timestamp on update current_timestamp,
foreign key (user_id) references member_basic(user_id) ON DELETE CASCADE
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
