-- 討論區
CREATE TABLE Games (
    game_id INT AUTO_INCREMENT PRIMARY KEY,
    game_title VARCHAR(255) NOT NULL,
    game_description TEXT NOT NULL,
    game_genre VARCHAR(100) NOT NULL,
    release_date DATE NOT NULL,
    game_platform VARCHAR(100) NOT NULL,
    poster VARCHAR(255) ,
    developer VARCHAR(255) NOT NULL
);

CREATE TABLE animations (
    animation_id INT AUTO_INCREMENT PRIMARY KEY,
    animation_title VARCHAR(255) NOT NULL,
    animation_description TEXT NOT NULL,
    episodes INT NOT NULL, -- 集數定義為整數類型
    release_date DATE NOT NULL,
    animation_genre VARCHAR(100) NOT NULL,
    animation_studio VARCHAR(100) NOT NULL,
    poster VARCHAR(255), -- 海報圖片 URL
    voice_actors TEXT -- 聲優
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Movies (
    movie_id INT AUTO_INCREMENT PRIMARY KEY,      
    movie_title VARCHAR(255) NOT NULL,          
    movie_description TEXT NOT NULL,             
    release_date DATE NOT NULL,                  
    movie_genre VARCHAR(255) NOT NULL,            
    director VARCHAR(100) NOT NULL,               
    cast TEXT NOT NULL,                          
    rating DECIMAL(3, 2) DEFAULT 0.00,            
    poster VARCHAR(255) NOT NULL                 
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



-- 文章表
CREATE TABLE Posts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,                 -- 文章 ID，主鍵
    title VARCHAR(255) NOT NULL,                            -- 文章標題
    body TEXT NOT NULL,                                     -- 文章內容
    author_id INT NOT NULL,                                 -- 作者 ID，外鍵
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, -- 創建時間
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL, -- 更新時間
    FOREIGN KEY (author_id) REFERENCES member_basic(user_id) ON DELETE CASCADE -- 外鍵，關聯 member_basic
);

-- 回覆表
CREATE TABLE Replies (
    reply_id INT AUTO_INCREMENT PRIMARY KEY,                -- 回覆 ID，主鍵
    post_id INT NOT NULL,                                   -- 文章 ID，外鍵
    body TEXT NOT NULL,                                     -- 回覆內容
    author_id INT NOT NULL,                                 -- 作者 ID，外鍵
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, -- 創建時間
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL, -- 更新時間
    FOREIGN KEY (post_id) REFERENCES Posts(post_id) ON DELETE CASCADE, -- 外鍵，關聯 Posts
    FOREIGN KEY (author_id) REFERENCES member_basic(user_id) ON DELETE CASCADE -- 外鍵，關聯 member_basic
);

-- 按讚表
CREATE TABLE Likes (
    like_id INT AUTO_INCREMENT PRIMARY KEY,                 -- 按讚 ID，主鍵
    post_id INT NOT NULL,                                   -- 文章 ID，外鍵
    user_id INT NOT NULL,                                   -- 用戶 ID，外鍵
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, -- 按讚時間
    posts_report TINYINT DEFAULT 0 NOT NULL,             -- 新增的欄位，可記錄 0 或 1
    FOREIGN KEY (post_id) REFERENCES Posts(post_id) ON DELETE CASCADE, -- 外鍵，關聯 Posts
    FOREIGN KEY (user_id) REFERENCES member_basic(user_id) ON DELETE CASCADE -- 外鍵，關聯 member_basic
);

INSERT INTO Games (game_title, game_description, game_genre, release_date, game_platform, poster, developer)
VALUES
('英雄傳說', '一款充滿史詩故事的角色扮演遊戲。', '角色扮演', '2022-03-01', 'PC', 'poster1.jpg', 'Falcom'),
('賽博忍者', '一款充滿動作感的賽博朋克遊戲。', '動作', '2021-11-12', 'PS5', 'poster2.jpg', '忍者軟體'),
('太空探險家', '在這款開放世界的冒險遊戲中探索宇宙。', '冒險', '2023-05-17', 'Xbox', 'poster3.jpg', '銀河遊戲公司'),
('喪屍末日', '在喪屍爆發中努力生存。', '恐怖', '2020-10-31', 'PC', 'poster4.jpg', '死亡像素工作室'),
('魔幻冒險', '展開一場充滿魔法的旅程。', '奇幻', '2021-06-20', 'Switch', 'poster5.jpg', '魔法工坊'),
('戰爭機器', '一款以未來戰爭為主題的射擊遊戲。', '射擊', '2022-12-05', 'PC', 'poster6.jpg', '鋼鐵戰士公司'),
('賽車傳奇', '挑戰全球最刺激的賽車賽事。', '競速', '2021-08-19', 'PS5', 'poster7.jpg', '速度之王'),
('忍者之影', '在黑暗中潛行的忍者冒險遊戲。', '動作', '2023-02-14', 'PC', 'poster8.jpg', '影子工作室'),
('王國之心', '一個結合魔幻和冒險的遊戲。', '冒險', '2021-09-25', 'Switch', 'poster9.jpg', '心之王國工作室'),
('未來之戰', '在未來世界中發生的激烈戰爭。', '科幻', '2022-01-01', 'Xbox', 'poster10.jpg', '未來科技'),
('生存之夜', '在黑夜中挑戰極限生存。', '冒險', '2023-03-12', 'PC', 'poster11.jpg', '夜行者公司'),
('魔獸王國', '一款充滿傳奇故事的奇幻遊戲。', '奇幻', '2022-07-08', 'Switch', 'poster12.jpg', '魔獸工作室'),
('賭命對決', '一場緊張刺激的卡牌遊戲對決。', '策略', '2021-04-28', 'PC', 'poster13.jpg', '卡牌大師'),
('飛天英雄', '控制超級英雄在天空中飛行和戰鬥。', '動作', '2022-09-18', 'PS5', 'poster14.jpg', '天空工作室'),
('傳奇足球', '體驗最真實的足球比賽。', '運動', '2023-06-01', 'PC', 'poster15.jpg', '足球巨星工作室');

INSERT INTO animations (animation_title, animation_description, episodes, release_date, animation_genre, animation_studio, poster, voice_actors)
VALUES
('刀劍神域', '一款虛擬實境遊戲中的生死冒險。', 25, '2020-07-15', '科幻', 'A1影業', 'poster1.jpg', '松岡禎丞、戶松遙'),
('鬼滅之刃', '描述少年炭治郎對抗惡鬼的故事。', 26, '2019-04-06', '奇幻', 'ufotable', 'poster2.jpg', '花江夏樹、鬼頭明里'),
('進擊的巨人', '人類對抗巨人的史詩戰爭。', 75, '2013-04-07', '動作', 'WIT工作室', 'poster3.jpg', '梶裕貴、石川由依'),
('輝夜姬想讓人告白', '兩位學生會會長的戀愛頭腦戰。', 12, '2019-01-12', '愛情', 'A1影業', 'poster4.jpg', '古賀葵、古川慎'),
('Re:從零開始的異世界生活', '少年無限次輪迴的異世界冒險。', 50, '2016-04-04', '奇幻', 'WHITE FOX', 'poster5.jpg', '小林裕介、高橋李依'),
('你的名字', '一場跨越時空的愛情故事。', 1, '2016-08-26', '愛情', 'CoMix Wave Films', 'poster6.jpg', '神木隆之介、上白石萌音'),
('我的英雄學院', '描述擁有超能力學生的英雄故事。', 88, '2016-04-03', '動作', 'BONES', 'poster7.jpg', '山下大輝、岡本信彥'),
('東京喰種', '描述人類與喰種之間的生存故事。', 48, '2014-07-04', '恐怖', 'Pierrot', 'poster8.jpg', '花江夏樹、雨宮天'),
('青春豬頭少年', '青春校園的奇幻故事。', 13, '2018-10-04', '奇幻', 'CloverWorks', 'poster9.jpg', '石川界人、瀨戶麻沙美'),
('化物語', '描述一位高中生與怪異現象的故事。', 15, '2009-07-03', '奇幻', 'SHAFT', 'poster10.jpg', '神谷浩史、齋藤千和'),
('魔法少女小圓', '顛覆傳統的魔法少女動畫。', 12, '2011-01-07', '奇幻', 'SHAFT', 'poster11.jpg', '悠木碧、斎藤千和'),
('未來日記', '一場以生存為目的的手機遊戲。', 26, '2011-10-09', '科幻', 'Asread', 'poster12.jpg', '富樫美鈴、白石稔'),
('全職獵人', '一位少年成為獵人的冒險故事。', 148, '2011-10-02', '冒險', 'Madhouse', 'poster13.jpg', '潘惠美、伊瀬茉莉也'),
('約定的夢幻島', '一群孩子逃離孤兒院的冒險。', 23, '2019-01-11', '驚悚', 'CloverWorks', 'poster14.jpg', '諸星堇、內田真禮'),
('ONE PIECE', '海賊王的冒險故事。', 1000, '1999-10-20', '冒險', '東映動畫', 'poster15.jpg', '田中真弓、中井和哉');

INSERT INTO Movies (movie_title, movie_description, release_date, movie_genre, director, cast, rating, poster)
VALUES
('寄生上流', '講述一個貧窮家庭攀附上流社會的故事。', '2019-05-30', '劇情', '奉俊昊', '宋康昊、李善均、崔宇植、朴素丹', 8.6, 'poster1.jpg'),
('你的名字', '一場跨越時空的愛情故事。', '2016-08-26', '愛情', '新海誠', '神木隆之介、上白石萌音', 8.9, 'poster2.jpg'),
('復仇者聯盟', '一群超級英雄聯手對抗威脅地球的敵人。', '2012-04-25', '動作', '喬斯·溫登', '小勞勃·道尼、克里斯·埃文斯、史嘉蕾·喬韓森', 8.0, 'poster3.jpg'),
('冰雪奇緣', '兩個姐妹之間的愛情與冒險故事。', '2013-11-27', '動畫', '克里斯·巴克', '伊迪娜·門澤爾、克里斯汀·貝爾', 7.5, 'poster4.jpg'),
('黑暗騎士', '蝙蝠俠與小丑的最終對決。', '2008-07-18', '動作', '克里斯托弗·諾蘭', '克里斯蒂安·貝爾、希斯·萊傑', 9.0, 'poster5.jpg'),
('神隱少女', '小女孩千尋進入神秘的靈異世界。', '2001-07-20', '奇幻', '宮崎駿', '柊瑠美、入野自由', 8.6, 'poster6.jpg'),
('泰坦尼克號', '一對戀人在災難中萌生的愛情故事。', '1997-12-19', '愛情', '詹姆斯·卡麥隆', '李奧納多·狄卡皮歐、凱特·溫絲蕾', 8.7, 'poster7.jpg'),
('蟻人', '一位擁有縮小能力的超級英雄。', '2015-07-17', '科幻', '派頓·瑞德', '保羅·路德、伊凡潔琳·莉莉', 7.3, 'poster8.jpg'),
('魔戒三部曲：王者再臨', '中土大陸的史詩最終章。', '2003-12-17', '奇幻', '彼得·傑克森', '伊恩·麥克連、維果·莫天森', 9.1, 'poster9.jpg'),
('功夫熊貓', '一隻愛做夢的熊貓成為武林高手。', '2008-06-06', '動畫', '馬克·奧斯本', '傑克·布萊克、達斯汀·霍夫曼', 7.5, 'poster10.jpg'),
('全面啟動', '一場在夢境中進行的偷竊行動。', '2010-07-16', '科幻', '克里斯托弗·諾蘭', '李奧納多·狄卡皮歐、艾倫·佩吉', 8.8, 'poster11.jpg'),
('蜘蛛人：無家日', '蜘蛛人面對多重宇宙的危機。', '2021-12-17', '超級英雄', '喬·沃茲', '湯姆·霍蘭德、辛蒂亞', 8.2, 'poster12.jpg'),
('捍衛戰士：獨行俠', '經典飛行員故事的延續。', '2022-05-27', '動作', '喬瑟夫·柯辛斯基', '湯姆·克魯斯、珍妮佛·康納莉', 8.4, 'poster13.jpg'),
('怪物公司', '怪物們的搞笑冒險故事。', '2001-11-02', '動畫', '彼得·多克特', '比利·克里斯托、約翰·古德曼', 8.1, 'poster14.jpg'),
('小丑', '描繪一名小丑逐漸走向瘋狂的過程。', '2019-10-04', '劇情', '陶德·菲利普斯', '瓦昆·菲尼克斯、勞勃·狄尼洛', 8.4, 'poster15.jpg');

INSERT INTO Posts (title, body, author_id)
VALUES
('程式設計的樂趣', '程式設計帶來快樂與成就感。', 1),
('大自然之美', '大自然是治癒與和平的來源。', 2),
('旅行日記：巴黎', '探索艾菲爾鐵塔及其他美景。', 3),
('2024 科技趨勢', '最新科技趨勢的概覽。', 4),
('健康生活小秘訣', '可以改善健康的日常習慣。', 5),
('烘焙的藝術', '烘焙既是藝術也是科學。', 6),
('攝影入門', '拍攝驚艷照片的基本技巧。', 7),
('人工智慧的崛起', '人工智慧如何塑造未來。', 8),
('正念與冥想', '正念如何改變你的生活。', 9),
('2024 健身目標', '設定並實現健身目標的方法。', 10),
('寵物照護指南', '照顧毛小孩的必備技巧。', 11),
('探索宇宙', '宇宙的奇妙之處。', 1),
('藝術史', '追溯藝術的演變過程。', 2),
('財務自由', '實現財務獨立的步驟。', 3),
('料理秘訣', '讓烹飪更簡單的小技巧。', 4),
('登山探險', '最佳徒步旅行路線推薦。', 5),
('學習新語言', '掌握語言的技巧。', 6),
('經典電影回顧', '最值得重溫的經典電影。', 7),
('閱讀的重要性', '閱讀如何豐富生活。', 8),
('如何提升生產力', '提高工作效率的關鍵方法。', 9),
('兒童教育指南', '幫助孩子快樂學習的方法。', 10),
('心靈成長之路', '自我提升的關鍵步驟。', 11),
('戶外活動好處', '戶外活動如何改善生活品質。', 1),
('職場軟技能', '如何培養有效的溝通能力。', 2),
('學習編程的理由', '學會編程如何影響你的未來。', 3),
('環保小貼士', '日常生活中的環保行動。', 4),
('如何開始寫日記', '用文字記錄生命的點滴。', 5),
('社交媒體的影響', '如何平衡社交媒體與現實生活。', 6),
('音樂的魅力', '音樂如何治癒心靈。', 7);

-- 插入 Replies 表
INSERT INTO Replies (post_id, body, author_id)
VALUES
(1, '非常同意，程式設計真的很有趣！', 2),
(2, '大自然的確是心靈的慰藉。', 3),
(3, '巴黎是我最想去的城市之一。', 4),
(4, '期待科技帶來更多便利！', 5),
(5, '這些健康習慣真的值得一試。', 6),
(6, '烘焙真的很療癒，謝謝分享！', 7),
(7, '這些攝影技巧幫了我不少忙！', 8),
(8, 'AI 的發展讓人又期待又擔憂。', 9),
(9, '正念練習真的很棒！', 10),
(10, '我明年也要設定健身目標！', 11),
(11, '寵物是人類最好的朋友。', 1),
(1, '程式設計真是一門無盡的藝術！', 2),
(2, '在大自然中散步讓人放鬆身心。', 3),
(3, '希望有機會能去巴黎旅行。', 4);

-- 插入 Likes 表
INSERT INTO Likes (post_id, user_id, posts_report)
VALUES
(1, 2, 0),
(2, 3, 0),
(3, 4, 0),
(4, 5, 0),
(5, 6, 0),
(6, 7, 0),
(7, 8, 0),
(8, 9, 0),
(9, 10, 0),
(10, 11, 0),
(11, 1, 0),
(1, 3, 1),
(2, 4, 0),
(3, 5, 1),
(4, 6, 0),
(5, 7, 0),
(6, 8, 0),
(7, 9, 1),
(8, 10, 0),
(9, 11, 1),
(10, 1, 0),
(11, 2, 0),
(1, 4, 1),
(2, 5, 0),
(3, 6, 0),
(4, 7, 0),
(5, 8, 1),
(6, 9, 0),
(7, 10, 0),
(8, 11, 1);


