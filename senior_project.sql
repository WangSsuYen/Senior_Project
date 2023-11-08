CREATE TABLE
    client (
        uniform_numbers VARCHAR(10) PRIMARY KEY COMMENT '統一編號',
        client_password VARCHAR(10) NOT NULL COMMENT '密碼',
        creattime datetime NOT NULL COMMENT '創建時間'
    ) COMMENT '客戶資料';

--建立餐廳資訊明細表

CREATE TABLE
    client_detail (
        uniform_numbers VARCHAR(10) NOT NULL COMMENT '統一編號',
        co_image TEXT NOT NULL COMMENT '公司圖片',
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

ALTER TABLE
    client_detail MODIFY co_image TEXT NOT NULL COMMENT '公司圖片';

-- 建立店家菜單表

CREATE TABLE
    client_menu (
        meals_number INT NOT NULL AUTO_INCREMENT COMMENT '餐點編號',
        meals_image TEXT NOT NULL COMMENT '餐點圖片',
        meals_name VARCHAR(10) NOT NULL COMMENT '餐點名稱',
        meals_price INT NOT NULL COMMENT '餐點價格',
        meals_description VARCHAR(50) NOT NULL COMMENT '餐點描述',
        meals_status VARCHAR(2) NOT NULL COMMENT '餐點狀態',
        meals_category INT NOT NULL COMMENT '餐點類別',
        meals_owner VARCHAR(15) NOT NULL COMMENT '餐點歸屬餐廳',
        meals_creattime datetime NOT NULL COMMENT '創建時間',
        PRIMARY KEY (meals_number),
        FOREIGN KEY (meals_owner) REFERENCES client(uniform_numbers),
        FOREIGN KEY (meals_category) REFERENCES meals_category(category_number)
    ) COMMENT '餐點資訊';


CREATE TABLE meals_category (
    category_number INT NOT NULL COMMENT '餐點類別編號',
    category_name VARCHAR(10) NOT NULL COMMENT '餐點類別名稱',
    category_creator VARCHAR(10) NOT NULL COMMENT '創建者',
    PRIMARY KEY (category_number),
    FOREIGN KEY (category_creator) REFERENCES client(uniform_numbers)
) COMMENT '餐點類別';



ALTER TABLE
    client_menu CHANGE meals_number meals_number INT NOT NULL AUTO_INCREMENT COMMENT '餐點編號';
ALTER TABLE
    client_menu CHANGE meals_category meals_category INT NOT NULL COMMENT '餐點類別';