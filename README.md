# 清茶坊 & 三分糖

这是一个基于Flask的电商网站，集成了推荐系统功能。系统可以跟踪用户行为，并根据用户行为提供个性化推荐。

## 功能特点

1. 商品展示
   - 首页显示20件商品
   - 商品详情页
   - 购物车功能

2. 推荐系统
   - 基于协同过滤的推荐算法
   - 在商品详情页显示推荐商品
   - 跟踪用户行为数据

3. 用户系统
   - 用户注册和登录
   - 管理员后台
   - 数据统计和分析

## 安装步骤

1. 克隆项目
```bash
git clone [项目地址]
cd [项目目录]
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 初始化数据库
```bash
python -m app.utils.init_db
```

5. 运行应用
```bash
python run.py
```

## 默认账户

- 管理员账户
  - 用户名：admin
  - 密码：admin123

- 测试用户账户
  - 用户名：test
  - 密码：test123

## 项目结构

```
app/
├── __init__.py          # 应用初始化
├── models/              # 数据模型
├── routes/              # 路由处理
├── static/              # 静态文件
│   ├── css/            # 样式文件
│   ├── js/             # JavaScript文件
│   └── images/         # 图片文件
├── templates/           # HTML模板
└── utils/              # 工具函数
    ├── init_db.py      # 数据库初始化
    └── recommender.py  # 推荐系统
```

## 技术栈

- 后端：Flask
- 数据库：SQLite
- 前端：Bootstrap 5
- 推荐算法：协同过滤

## 注意事项

1. 首次运行前请确保已安装所有依赖
2. 需要先运行数据库初始化脚本
3. 商品图片需要放在 `app/static/images` 目录下
4. 默认使用SQLite数据库，数据文件为 `shop.db` 