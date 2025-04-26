from app import db
from datetime import datetime
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 产品详细信息
    product_features = db.Column(db.Text)  # 产品特点
    objective_analysis = db.Column(db.Text)  # 客观参数分析
    drinking_suggestions = db.Column(db.Text)  # 科学饮用建议
    ingredients = db.Column(db.Text)  # 配料表
    origin = db.Column(db.Text)  # 产地信息
    specifications = db.Column(db.Text)  # 规格参数
    suitable_crowd = db.Column(db.Text)  # 适宜人群
    
    # 原有字段保留
    flavor_profile = db.Column(db.Text)    # 口味分析
    texture_description = db.Column(db.Text)  # 口感描述
    after_taste = db.Column(db.Text)       # 饮后感受
    mood_trigger = db.Column(db.Text)      # 情绪触发
    drinking_scenario = db.Column(db.Text)  # 饮用场景建议
    flavor_association = db.Column(db.Text)  # 风味联想

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_purchased = db.Column(db.Boolean, default=False)  # 是否已结算
    
    # 添加关系
    product = db.relationship('Product', backref='cart_items')
    user = db.relationship('User', backref='cart_items')

class UserBehavior(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    behavior_type = db.Column(db.String(20), nullable=False)  # view, click, purchase
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Integer)  # 停留时间（秒）
    is_recommended = db.Column(db.Boolean, default=False)  # 是否是详情页推荐的商品 