--建立客戶資料表
CREATE TABLE client (
        uniform_numbers INT PRIMARY KEY COMMENT '統一編號',
        client_password VARCHAR(10) NOT NULL COMMENT '密碼',
        creattime datetime NOT NULL COMMENT '創建時間',
    );

--修改欄位型態
ALTER TABLE client MODIFY COLUMN uniform_numbers VARCHAR(10);

--建立餐廳資訊明細表
CREATE TABLE
    client_detail (
        uniform_numbers VARCHAR(10) NOT NULL COMMENT '統一編號',
        co_image VARCHAR(10) NOT NULL COMMENT '公司圖片',
        rest_name VARCHAR(10) NOT NULL COMMENT '餐廳名稱',
        rest_address VARCHAR(15) NOT NULL COMMENT '餐廳地址',
        rest_manager VARCHAR(5) NOT NULL COMMENT '餐廳負責人',
        rest_phone VARCHAR(15) NOT NULL COMMENT '餐廳電話',
        co_name VARCHAR(10) NOT NULL COMMENT '公司名稱',
        co_address VARCHAR(15) NOT NULL COMMENT '公司地址',
        co_owner VARCHAR(15) NOT NULL COMMENT '公司負責人',
        owner_phone VARCHAR(15) NOT NULL COMMENT '餐廳電話',
        PRIMARY KEY (uniform_numbers),
        FOREIGN KEY (uniform_numbers) REFERENCES client(uniform_numbers)
    ) COMMENT '餐廳資訊';
