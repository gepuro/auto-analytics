-- Auto Analytics Database Initialization
-- POS会員証システム用テストデータ

-- テーブル削除（存在する場合）
DROP TABLE IF EXISTS transaction_items;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS stores;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS users;

-- 会員テーブル
CREATE TABLE members (
    member_id SERIAL PRIMARY KEY,
    member_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    name_kana VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    postal_code VARCHAR(10),
    address TEXT,
    birth_date DATE,
    gender CHAR(1) CHECK (gender IN ('M', 'F')),
    member_rank VARCHAR(20) DEFAULT 'Bronze' CHECK (member_rank IN ('Bronze', 'Silver', 'Gold', 'Platinum')),
    points INTEGER DEFAULT 0,
    total_spent DECIMAL(12,2) DEFAULT 0,
    registration_date DATE DEFAULT CURRENT_DATE,
    last_visit_date DATE,
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive', 'Suspended')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 店舗テーブル
CREATE TABLE stores (
    store_id SERIAL PRIMARY KEY,
    store_code VARCHAR(20) UNIQUE NOT NULL,
    store_name VARCHAR(100) NOT NULL,
    postal_code VARCHAR(10),
    address TEXT,
    phone VARCHAR(20),
    manager_name VARCHAR(100),
    opening_hours VARCHAR(50),
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive', 'Maintenance')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 商品テーブル
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_code VARCHAR(30) UNIQUE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50),
    unit_price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2),
    supplier VARCHAR(100),
    description TEXT,
    is_taxable BOOLEAN DEFAULT TRUE,
    tax_rate DECIMAL(5,4) DEFAULT 0.1000,
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive', 'Discontinued')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 取引テーブル
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    transaction_code VARCHAR(30) UNIQUE NOT NULL,
    store_id INTEGER REFERENCES stores(store_id),
    member_id INTEGER REFERENCES members(member_id),
    transaction_date TIMESTAMP NOT NULL,
    cashier_name VARCHAR(100),
    subtotal DECIMAL(12,2) NOT NULL,
    tax_amount DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    points_used INTEGER DEFAULT 0,
    points_earned INTEGER DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    receipt_number VARCHAR(50),
    status VARCHAR(20) DEFAULT 'Completed' CHECK (status IN ('Completed', 'Cancelled', 'Refunded')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 取引明細テーブル
CREATE TABLE transaction_items (
    item_id SERIAL PRIMARY KEY,
    transaction_id INTEGER REFERENCES transactions(transaction_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_rate DECIMAL(5,4) DEFAULT 0,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    subtotal DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 既存のusersテーブル（tools.yamlで参照されている）
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- インデックス作成
CREATE INDEX idx_members_code ON members(member_code);
CREATE INDEX idx_members_email ON members(email);
CREATE INDEX idx_members_rank ON members(member_rank);
CREATE INDEX idx_members_status ON members(status);

CREATE INDEX idx_stores_code ON stores(store_code);
CREATE INDEX idx_stores_status ON stores(status);

CREATE INDEX idx_products_code ON products(product_code);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_status ON products(status);

CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_store ON transactions(store_id);
CREATE INDEX idx_transactions_member ON transactions(member_id);
CREATE INDEX idx_transactions_status ON transactions(status);

CREATE INDEX idx_transaction_items_transaction ON transaction_items(transaction_id);
CREATE INDEX idx_transaction_items_product ON transaction_items(product_id);

-- 会員データ挿入
INSERT INTO members (member_code, name, name_kana, email, phone, postal_code, address, birth_date, gender, member_rank, points, total_spent, registration_date, last_visit_date) VALUES
('M001', '田中太郎', 'タナカタロウ', 'tanaka.taro@example.com', '090-1234-5678', '100-0001', '東京都千代田区千代田1-1-1', '1985-03-15', 'M', 'Gold', 2500, 98500.00, '2023-01-15', '2024-12-15'),
('M002', '佐藤花子', 'サトウハナコ', 'sato.hanako@example.com', '080-2345-6789', '150-0001', '東京都渋谷区神宮前1-2-3', '1990-07-22', 'F', 'Silver', 1800, 75200.00, '2023-02-10', '2024-12-10'),
('M003', '鈴木一郎', 'スズキイチロウ', 'suzuki.ichiro@example.com', '070-3456-7890', '160-0023', '東京都新宿区西新宿2-3-4', '1982-11-08', 'M', 'Platinum', 5200, 185000.00, '2022-11-20', '2024-12-20'),
('M004', '高橋美咲', 'タカハシミサキ', 'takahashi.misaki@example.com', '090-4567-8901', '140-0002', '東京都品川区東品川3-4-5', '1993-05-14', 'F', 'Bronze', 450, 18500.00, '2024-03-01', '2024-11-28'),
('M005', '伊藤健太', 'イトウケンタ', 'ito.kenta@example.com', '080-5678-9012', '104-0061', '東京都中央区銀座4-5-6', '1988-09-30', 'M', 'Gold', 3100, 125000.00, '2023-05-15', '2024-12-12'),
('M006', '山田由美', 'ヤマダユミ', 'yamada.yumi@example.com', '070-6789-0123', '170-0013', '東京都豊島区東池袋1-6-7', '1991-12-25', 'F', 'Silver', 1950, 82000.00, '2023-08-20', '2024-12-08'),
('M007', '中村大輔', 'ナカムラダイスケ', 'nakamura.daisuke@example.com', '090-7890-1234', '130-0015', '東京都墨田区横網2-7-8', '1987-04-12', 'M', 'Bronze', 320, 15800.00, '2024-06-10', '2024-11-25'),
('M008', '小林さくら', 'コバヤシサクラ', 'kobayashi.sakura@example.com', '080-8901-2345', '110-0005', '東京都台東区上野3-8-9', '1994-08-07', 'F', 'Gold', 2800, 112000.00, '2023-03-25', '2024-12-14'),
('M009', '加藤雄一', 'カトウユウイチ', 'kato.yuichi@example.com', '070-9012-3456', '190-0012', '東京都立川市曙町1-9-10', '1983-01-20', 'M', 'Silver', 1650, 68500.00, '2023-09-12', '2024-12-05'),
('M010', '松本恵子', 'マツモトケイコ', 'matsumoto.keiko@example.com', '090-0123-4567', '120-0034', '東京都足立区千住2-10-11', '1989-06-18', 'F', 'Platinum', 4850, 195000.00, '2022-12-08', '2024-12-18');

-- 店舗データ挿入
INSERT INTO stores (store_code, store_name, postal_code, address, phone, manager_name, opening_hours) VALUES
('S001', '銀座本店', '104-0061', '東京都中央区銀座1-1-1', '03-1234-5678', '店長 田中', '10:00-22:00'),
('S002', '新宿店', '160-0022', '東京都新宿区新宿3-2-1', '03-2345-6789', '店長 佐藤', '10:00-21:00'),
('S003', '渋谷店', '150-0041', '東京都渋谷区神南1-3-1', '03-3456-7890', '店長 鈴木', '11:00-23:00'),
('S004', '池袋店', '170-0013', '東京都豊島区東池袋1-4-1', '03-4567-8901', '店長 高橋', '10:00-22:00'),
('S005', '上野店', '110-0005', '東京都台東区上野2-5-1', '03-5678-9012', '店長 伊藤', '09:00-21:00');

-- 商品データ挿入
INSERT INTO products (product_code, product_name, category, subcategory, unit_price, cost_price, supplier) VALUES
-- 食品
('P001', 'おにぎり（鮭）', '食品', 'おにぎり', 150.00, 80.00, '食品卸売A'),
('P002', 'おにぎり（梅）', '食品', 'おにぎり', 140.00, 75.00, '食品卸売A'),
('P003', 'サンドイッチ（ハム&チーズ）', '食品', 'サンドイッチ', 280.00, 150.00, '食品卸売B'),
('P004', 'コーヒー（ホット）', '飲料', 'ホット', 120.00, 50.00, '飲料卸売A'),
('P005', '緑茶（ペットボトル）', '飲料', 'ペットボトル', 150.00, 80.00, '飲料卸売A'),
('P006', 'お弁当（から揚げ）', '食品', '弁当', 580.00, 320.00, '食品卸売C'),
('P007', 'お弁当（幕の内）', '食品', '弁当', 650.00, 380.00, '食品卸売C'),
('P008', 'パン（メロンパン）', '食品', 'パン', 180.00, 90.00, 'パン工房A'),
('P009', 'パン（クロワッサン）', '食品', 'パン', 220.00, 110.00, 'パン工房A'),
('P010', 'アイスクリーム（バニラ）', '食品', 'アイス', 250.00, 120.00, '冷凍食品卸売A'),

-- 日用品
('P011', 'ティッシュペーパー', '日用品', '紙製品', 198.00, 120.00, '日用品卸売A'),
('P012', 'トイレットペーパー（4ロール）', '日用品', '紙製品', 380.00, 220.00, '日用品卸売A'),
('P013', 'シャンプー（500ml）', '日用品', 'ヘアケア', 680.00, 400.00, '化粧品卸売A'),
('P014', '歯ブラシ', '日用品', 'オーラルケア', 120.00, 60.00, '日用品卸売B'),
('P015', '歯磨き粉', '日用品', 'オーラルケア', 280.00, 150.00, '日用品卸売B'),
('P016', 'ハンドソープ', '日用品', '洗剤', 320.00, 180.00, '日用品卸売A'),
('P017', '洗濯洗剤（1kg）', '日用品', '洗剤', 480.00, 280.00, '日用品卸売A'),
('P018', 'マスク（50枚入り）', '日用品', '衛生用品', 980.00, 550.00, '衛生用品卸売A'),
('P019', '電池（単3・4本）', '日用品', '電池', 380.00, 200.00, '電器卸売A'),
('P020', 'ボールペン（黒）', '文具', '筆記用具', 120.00, 60.00, '文具卸売A'),

-- 衣料品
('P021', 'Tシャツ（白・Mサイズ）', '衣料品', 'トップス', 1980.00, 1100.00, 'アパレル卸売A'),
('P022', 'Tシャツ（黒・Lサイズ）', '衣料品', 'トップス', 1980.00, 1100.00, 'アパレル卸売A'),
('P023', 'ジーンズ（ブルー・Mサイズ）', '衣料品', 'ボトムス', 3980.00, 2200.00, 'アパレル卸売B'),
('P024', '靴下（白・3足組）', '衣料品', '下着・靴下', 580.00, 320.00, 'アパレル卸売C'),
('P025', '下着（Mサイズ）', '衣料品', '下着・靴下', 1280.00, 700.00, 'アパレル卸売C'),

-- 家電・雑貨
('P026', 'イヤホン（有線）', '家電', 'オーディオ', 1580.00, 800.00, '家電卸売A'),
('P027', '充電ケーブル（USB-C）', '家電', 'アクセサリ', 980.00, 500.00, '家電卸売A'),
('P028', 'スマートフォンケース', '家電', 'アクセサリ', 1280.00, 650.00, '家電卸売B'),
('P029', 'ノート（A4・80枚）', '文具', 'ノート', 280.00, 150.00, '文具卸売A'),
('P030', 'クリアファイル（A4・10枚）', '文具', 'ファイル', 180.00, 90.00, '文具卸売A');

-- usersテーブルにもサンプルデータを挿入
INSERT INTO users (name, age, email) VALUES
('田中太郎', 39, 'tanaka.taro@example.com'),
('佐藤花子', 34, 'sato.hanako@example.com'),
('鈴木一郎', 42, 'suzuki.ichiro@example.com'),
('高橋美咲', 31, 'takahashi.misaki@example.com'),
('伊藤健太', 36, 'ito.kenta@example.com');

-- 取引データ挿入（過去6ヶ月分のサンプル）
INSERT INTO transactions (transaction_code, store_id, member_id, transaction_date, cashier_name, subtotal, tax_amount, discount_amount, points_used, points_earned, total_amount, payment_method, receipt_number) VALUES
-- 12月のデータ
('T20241215001', 1, 1, '2024-12-15 14:30:00', '山田', 1500.00, 150.00, 0.00, 0, 15, 1650.00, 'クレジットカード', 'R241215001'),
('T20241214001', 2, 2, '2024-12-14 10:15:00', '鈴木', 850.00, 85.00, 50.00, 100, 8, 885.00, '現金', 'R241214001'),
('T20241213001', 3, 3, '2024-12-13 18:45:00', '田中', 3200.00, 320.00, 200.00, 0, 32, 3320.00, 'クレジットカード', 'R241213001'),
('T20241212001', 1, 4, '2024-12-12 12:20:00', '佐藤', 680.00, 68.00, 0.00, 0, 7, 748.00, '電子マネー', 'R241212001'),
('T20241211001', 4, 5, '2024-12-11 16:10:00', '高橋', 2200.00, 220.00, 100.00, 50, 22, 2370.00, 'クレジットカード', 'R241211001'),

-- 11月のデータ
('T20241125001', 2, 1, '2024-11-25 13:25:00', '伊藤', 1200.00, 120.00, 0.00, 0, 12, 1320.00, '現金', 'R241125001'),
('T20241124001', 3, 6, '2024-11-24 11:40:00', '山田', 890.00, 89.00, 30.00, 0, 9, 948.00, '電子マネー', 'R241124001'),
('T20241123001', 1, 7, '2024-11-23 15:55:00', '鈴木', 450.00, 45.00, 0.00, 0, 5, 495.00, '現金', 'R241123001'),
('T20241122001', 5, 8, '2024-11-22 09:30:00', '田中', 1800.00, 180.00, 80.00, 0, 18, 1900.00, 'クレジットカード', 'R241122001'),
('T20241121001', 4, 9, '2024-11-21 17:15:00', '佐藤', 1350.00, 135.00, 0.00, 25, 14, 1460.00, '電子マネー', 'R241121001'),

-- 10月のデータ
('T20241015001', 1, 10, '2024-10-15 14:20:00', '高橋', 2800.00, 280.00, 150.00, 0, 28, 2930.00, 'クレジットカード', 'R241015001'),
('T20241014001', 2, 1, '2024-10-14 12:35:00', '伊藤', 720.00, 72.00, 0.00, 0, 7, 792.00, '現金', 'R241014001'),
('T20241013001', 3, 2, '2024-10-13 16:50:00', '山田', 1650.00, 165.00, 100.00, 50, 17, 1665.00, '電子マネー', 'R241013001'),
('T20241012001', 4, 3, '2024-10-12 10:25:00', '鈴木', 3500.00, 350.00, 200.00, 0, 35, 3650.00, 'クレジットカード', 'R241012001'),
('T20241011001', 5, 4, '2024-10-11 18:10:00', '田中', 980.00, 98.00, 0.00, 0, 10, 1078.00, '現金', 'R241011001');

-- 取引明細データ挿入
INSERT INTO transaction_items (transaction_id, product_id, quantity, unit_price, discount_rate, discount_amount, subtotal) VALUES
-- T20241215001の明細
(1, 1, 2, 150.00, 0, 0, 300.00),
(1, 4, 1, 120.00, 0, 0, 120.00),
(1, 6, 1, 580.00, 0, 0, 580.00),
(1, 11, 1, 198.00, 0, 0, 198.00),
(1, 20, 2, 120.00, 0, 0, 240.00),
(1, 29, 1, 280.00, 0, 0, 280.00),

-- T20241214001の明細
(2, 2, 1, 140.00, 0, 0, 140.00),
(2, 5, 1, 150.00, 0, 0, 150.00),
(2, 8, 1, 180.00, 0, 0, 180.00),
(2, 14, 2, 120.00, 0, 0, 240.00),
(2, 19, 1, 380.00, 0.05, 19.00, 361.00),

-- T20241213001の明細
(3, 21, 1, 1980.00, 0, 0, 1980.00),
(3, 23, 1, 3980.00, 0.05, 199.00, 3781.00),
(3, 24, 2, 580.00, 0, 0, 1160.00),

-- T20241212001の明細
(4, 3, 1, 280.00, 0, 0, 280.00),
(4, 4, 2, 120.00, 0, 0, 240.00),
(4, 12, 1, 380.00, 0, 0, 380.00),

-- T20241211001の明細
(5, 26, 1, 1580.00, 0, 0, 1580.00),
(5, 27, 1, 980.00, 0.1, 98.00, 882.00),
(5, 16, 1, 320.00, 0, 0, 320.00),

-- 他の取引の明細も追加
(6, 7, 1, 650.00, 0, 0, 650.00),
(6, 5, 2, 150.00, 0, 0, 300.00),
(6, 15, 1, 280.00, 0, 0, 280.00),

(7, 9, 2, 220.00, 0, 0, 440.00),
(7, 4, 1, 120.00, 0, 0, 120.00),
(7, 13, 1, 680.00, 0.04, 27.20, 652.80),

(8, 1, 1, 150.00, 0, 0, 150.00),
(8, 2, 1, 140.00, 0, 0, 140.00),
(8, 4, 1, 120.00, 0, 0, 120.00),

(9, 22, 1, 1980.00, 0, 0, 1980.00),
(9, 25, 1, 1280.00, 0.06, 76.80, 1203.20),

(10, 6, 2, 580.00, 0, 0, 1160.00),
(10, 17, 1, 480.00, 0, 0, 480.00),

(11, 28, 1, 1280.00, 0, 0, 1280.00),
(11, 30, 5, 180.00, 0.05, 45.00, 855.00),
(11, 18, 1, 980.00, 0, 0, 980.00),

(12, 10, 3, 250.00, 0, 0, 750.00),

(13, 7, 1, 650.00, 0, 0, 650.00),
(13, 5, 3, 150.00, 0, 0, 450.00),
(13, 11, 2, 198.00, 0.1, 39.60, 356.40),
(13, 20, 2, 120.00, 0, 0, 240.00),

(14, 21, 1, 1980.00, 0, 0, 1980.00),
(14, 23, 1, 3980.00, 0.05, 199.00, 3781.00),

(15, 8, 2, 180.00, 0, 0, 360.00),
(15, 4, 3, 120.00, 0, 0, 360.00),
(15, 15, 1, 280.00, 0, 0, 280.00);

-- 統計情報の更新
ANALYZE;

-- データベース初期化完了メッセージ
SELECT 'Auto Analytics POS Database initialized successfully!' as status,
       (SELECT COUNT(*) FROM members) as member_count,
       (SELECT COUNT(*) FROM stores) as store_count,
       (SELECT COUNT(*) FROM products) as product_count,
       (SELECT COUNT(*) FROM transactions) as transaction_count,
       (SELECT COUNT(*) FROM transaction_items) as transaction_item_count;