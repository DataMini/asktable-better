# 使用指南：编写符合格式的 `main.yaml` 描述文件

本文档为新用户提供编写 `main.yaml` 描述文件的指导，`main.yaml` 是测试场景的核心配置文件，定义了数据源、初始化配置、业务知识以及测试用例。

---

## 文件结构概览

```yaml
data:
  name_cn: <测试集名称>  # 测试集的中文名称
  bot_name_cn: <机器人中文名称>  # 机器人的中文名称
  local_file: <本地文件路径>  # 可选，本地 Excel 数据文件路径
  access_config:  # 可选，数据库连接配置
    host: <数据库地址>
    port: <数据库端口>
    user: <用户名>
    password: <密码>
    db: <数据库名称>
  init_sqls:  # 数据库初始化 SQL 配置
    type: <http|local|skip>  # 可选值：http、local 或 skip
    location: <初始化 SQL 文件位置>  # URL 或本地路径
business_knowledge:  # 可选，业务知识配置
  glossary:
    - name: <术语名称>
      aliases:  # 别名，可选
        - <别名1>
        - <别名2>
      definition: <术语定义>
cases:  # 测试用例配置
  - name: <测试用例名称>
    type: chat  # 测试类型，固定为 chat
    params:
      question: <问题内容>
```

---

## 配置字段说明

### `data` 部分
#### 必填字段
- **name_cn**: 测试集的中文名称，例如 `GDP`。
- **bot_name_cn**: 机器人的中文名称，例如 `GDP数据查询小助手`。

#### 可选字段
- **local_file**: 用于指定本地的 Excel 文件路径，例如 `./2019GDP数据.xlsx`。
- **access_config**: 如果使用数据库作为数据源，需配置数据库连接信息。
  - `host`: 数据库地址，例如 `mysql8.test.dminfra.cn`。
  - `port`: 数据库端口号，例如 `3006`。
  - `user`: 数据库用户名，例如 `at_test`。
  - `password`: 数据库密码，例如 `c65b1d2edb2f19476ec3`。
  - `db`: 数据库名称，例如 `stock`。
- **init_sqls**: 数据库初始化 SQL 文件配置。
  - `type`: 初始化方式，可选值包括：
    - `http`: 远程下载并执行 SQL 文件。
    - `local`: 使用本地路径执行 SQL 文件。
    - `skip`: 跳过数据库初始化。
  - `location`: SQL 文件的远程 URL 或本地路径。

---

### `business_knowledge` 部分
#### 可选字段
- **glossary**: 用于定义业务术语。
  - **name**: 术语名称，例如 `销冠`。
  - **aliases**: 术语的别名列表，例如 `销售冠军`。
  - **definition**: 术语的定义，例如 `在一个时间段内，总销售额最高的人`。

---

### `cases` 部分
#### 必填字段
- **name**: 测试用例名称，例如 `case_1`。
- **type**: 测试用例类型，固定为 `chat`。
- **params**:
  - **question**: 定义测试用例的问题内容，可以是单个字符串或字符串列表。

---

## 示例文件

### 示例 1：本地 Excel 数据文件
```yaml
data:
  name_cn: GDP
  bot_name_cn: GDP数据查询小助手
  local_file: ./2019GDP数据.xlsx
cases:
  - name: case_1
    type: chat
    params:
      question: 江苏GDP多少
  - name: case_2
    type: chat
    params:
      question: 广东和江苏的GDP差距多少
```

### 示例 2：远程初始化 SQL 文件
```yaml
data:
  name_cn: 股票数据问答
  bot_name_cn: 股票数据问答小助手
  access_config:
    host: 127.0.0.1
    port: 3306
    user: at_test
    password: at_test
    db: stock
  init_sqls:
    type: http
    location: https://example.com/init_sqls.tar.gz
cases:
  - name: case_1
    type: chat
    params:
      question: 查询股票600001的最新的交易记录
```

### 示例 3：本地初始化 SQL 文件
```yaml
data:
  name_cn: 基金销售问答
  bot_name_cn: 基金销售问答小助手
  access_config:
    host: 127.0.0.1
    port: 3306
    user: at_test
    password: at_test
    db: fund_sales
  init_sqls:
    type: local
    location: ./init_sqls/
business_knowledge:
  glossary:
    - name: 销冠
      aliases:
        - 销售冠军
      definition: 在一个时间段内，总销售额最高的人。
cases:
  - name: case_1
    type: chat
    params:
      question: 0号基金2024年总收入多少？具体到每个月分别是多少？
```

---

## 注意事项
1. **字段完整性**: 确保每个测试用例都包含 `name`、`type` 和 `params`。
2. **路径格式**:
   - 本地路径以 `./` 开头。
   - 远程路径需以 `http://` 或 `https://` 开头。
3. **测试类型**: 当前仅支持 `chat` 类型。

如需进一步帮助，请联系技术支持团队。
