CREATE TABLE if not exists products (
    product_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '产品ID',
    product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
    price DECIMAL(10, 2) NOT NULL COMMENT '产品价格',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT '产品表';

CREATE TABLE if not exists sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '销售员ID',
    salesperson_name VARCHAR(100) NOT NULL COMMENT '销售员姓名',
    phone VARCHAR(20) COMMENT '联系电话',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT '销售员表';

CREATE TABLE if not exists orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '订单ID',
    product_id INT NOT NULL COMMENT '产品ID',
    quantity INT NOT NULL COMMENT '产品数量',
    sale_id INT NOT NULL COMMENT '销售员ID',
    order_date DATE NOT NULL COMMENT '订单日期',
    total_amount DECIMAL(10, 2) NOT NULL COMMENT '订单总金额',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id)
) COMMENT '订单表';