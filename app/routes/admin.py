from flask import Blueprint, render_template, request, jsonify, redirect, url_for, send_file
from flask_login import login_required, current_user
from app.models.models import UserBehavior, Product, CartItem, User, db
from sqlalchemy import func
from functools import wraps
import json
import io
from datetime import datetime

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'status': 'error', 'message': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/')
@login_required
@admin_required
def index():
    return render_template('admin/index.html')

@admin.route('/stats')
@login_required
@admin_required
def stats():
    # 推荐产品加入购物车次数
    recommended_clicks = UserBehavior.query.filter_by(
        behavior_type='click',
        is_recommended=True
    ).count()
    
    # 推荐产品购买次数
    recommended_purchases = UserBehavior.query.filter_by(
        behavior_type='purchase',
        is_recommended=True
    ).count()

    # 推荐产品查看次数
    recommended_views = UserBehavior.query.filter_by(
        behavior_type='view',
        is_recommended=True
    ).count()
    
    # 获取推荐产品平均查看时间
    avg_duration = db.session.query(
        func.avg(UserBehavior.duration)
    ).filter(
        UserBehavior.behavior_type == 'view',
        UserBehavior.is_recommended == True
    ).scalar() or 0
    
    # 计算转化率 = 购买次数 / 查看次数
    conversion_rate = (recommended_purchases / recommended_views * 100) if recommended_views > 0 else 0
    
    # 计算总收入
    total_revenue = db.session.query(
        func.sum(Product.price * CartItem.quantity)
    ).join(
        CartItem, Product.id == CartItem.product_id
    ).filter(
        CartItem.is_purchased == True
    ).scalar() or 0
    
    # 计算推荐产品收入
    recommended_revenue = db.session.query(
        func.sum(Product.price * CartItem.quantity)
    ).join(
        CartItem, Product.id == CartItem.product_id
    ).join(
        UserBehavior,
        (Product.id == UserBehavior.product_id) &
        (UserBehavior.behavior_type == 'click') &
        (UserBehavior.is_recommended == True)
    ).filter(
        CartItem.is_purchased == True
    ).scalar() or 0
    
    # 计算推荐产品收入占比
    recommended_revenue_ratio = (recommended_revenue / total_revenue * 100) if total_revenue > 0 else 0
    
    # 获取用户总数
    total_users = User.query.count()
    
    # 获取商品总数
    total_products = Product.query.count()
    
    # 获取今日新增用户数
    today_users = User.query.filter(
        func.date(User.created_at) == func.current_date()
    ).count()
    
    stats = {
        'recommended_clicks': recommended_clicks,
        'recommended_views': recommended_views,
        'avg_duration': round(avg_duration, 2),
        'recommended_purchases': recommended_purchases,
        'conversion_rate': round(conversion_rate, 2),
        'total_revenue': round(total_revenue, 2),
        'recommended_revenue': round(recommended_revenue, 2),
        'recommended_revenue_ratio': round(recommended_revenue_ratio, 2),
        'total_users': total_users,
        'total_products': total_products,
        'today_users': today_users
    }
    
    return render_template('admin/stats.html', stats=stats)

@admin.route('/products')
@login_required
@admin_required
def products():
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    return redirect(url_for('admin.index'))

@admin.route('/product/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        try:
            data = request.get_json()
            product = Product(
                name=data['name'],
                category=data['category'],
                price=float(data['price']),
                description=data['description'],
                image_url=data.get('image_url', ''),
                features=data['features'],
                flavor_profile=data['flavor_profile'],
                texture=data['texture'],
                aftertaste=data['aftertaste'],
                mood_trigger=data['mood_trigger'],
                drinking_scenario=data['drinking_scenario'],
                flavor_association=data['flavor_association']
            )
            db.session.add(product)
            db.session.commit()
            return jsonify({'message': '商品添加成功', 'id': product.id}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    return render_template('admin/add_product.html')

@admin.route('/product/<int:product_id>', methods=['GET'])
@login_required
@admin_required
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'category': product.category,
        'price': product.price,
        'description': product.description,
        'image_url': product.image_url,
        'product_features': product.product_features,
        'flavor_profile': product.flavor_profile,
        'texture_description': product.texture_description,
        'after_taste': product.after_taste,
        'mood_trigger': product.mood_trigger,
        'drinking_scenario': product.drinking_scenario,
        'flavor_association': product.flavor_association
    })

@admin.route('/product/<int:product_id>', methods=['PUT'])
@login_required
@admin_required
def update_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        data = request.form
        
        product.name = data['name']
        product.category = data['category']
        product.price = float(data['price'])
        product.description = data['description']
        product.image_url = data.get('image_url', '')
        product.product_features = data.get('product_features', '')
        product.flavor_profile = data.get('flavor_profile', '')
        product.texture_description = data.get('texture_description', '')
        product.after_taste = data.get('after_taste', '')
        product.mood_trigger = data.get('mood_trigger', '')
        product.drinking_scenario = data.get('drinking_scenario', '')
        product.flavor_association = data.get('flavor_association', '')
        
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@admin.route('/product/<int:product_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@admin.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    
    # 获取每个用户的行为数据
    user_stats = {}
    for user in users:
        # 获取推荐产品加入购物车次数
        recommended_clicks = UserBehavior.query.filter_by(
            user_id=user.id,
            behavior_type='click',
            is_recommended=True
        ).count()
        
        # 获取推荐产品查看次数
        recommended_views = UserBehavior.query.filter_by(
            user_id=user.id,
            behavior_type='view',
            is_recommended=True
        ).count()
        
        # 获取推荐产品平均停留时间
        avg_duration = db.session.query(
            func.avg(UserBehavior.duration)
        ).filter(
            UserBehavior.user_id == user.id,
            UserBehavior.behavior_type == 'view',
            UserBehavior.is_recommended == True
        ).scalar() or 0
        
        # 获取推荐产品购买次数
        recommended_purchases = UserBehavior.query.filter_by(
            user_id=user.id,
            behavior_type='purchase',
            is_recommended=True
        ).count()
        
        # 计算转化率
        conversion_rate = (recommended_purchases / recommended_views * 100) if recommended_views > 0 else 0
        print(conversion_rate)
        
        # 计算总收入（包括已结算的购物车项）
        total_revenue = db.session.query(
            func.sum(Product.price * CartItem.quantity)
        ).join(
            CartItem, Product.id == CartItem.product_id
        ).filter(
            CartItem.user_id == user.id,
            CartItem.is_purchased == True
        ).scalar() or 0
        
        # 计算推荐产品收入
        recommended_revenue = db.session.query(
            func.sum(Product.price * CartItem.quantity)
        ).join(
            CartItem, Product.id == CartItem.product_id
        ).join(
            UserBehavior,
            (Product.id == UserBehavior.product_id) &
            (UserBehavior.user_id == user.id) &
            (UserBehavior.behavior_type == 'click') &
            (UserBehavior.is_recommended == True)
        ).filter(
            CartItem.is_purchased == True
        ).scalar() or 0
        
        # 计算推荐产品收入占比
        recommended_revenue_ratio = (recommended_revenue / total_revenue * 100) if total_revenue > 0 else 0
        
        user_stats[user.id] = {
            'recommended_clicks': recommended_clicks,
            'recommended_views': recommended_views,
            'avg_duration': round(avg_duration, 2),
            'recommended_purchases': recommended_purchases,
            'conversion_rate': round(conversion_rate, 2),
            'total_revenue': round(total_revenue, 2),
            'recommended_revenue': round(recommended_revenue, 2),
            'recommended_revenue_ratio': round(recommended_revenue_ratio, 2)
        }
    
    return render_template('admin/users.html', users=users, user_stats=user_stats)

@admin.route('/users/export')
@login_required
@admin_required
def export_users():
    # 获取所有用户行为数据
    user_behaviors = UserBehavior.query.all()
    
    # 获取所有用户和产品信息，用于关联
    users = {user.id: user for user in User.query.all()}
    products = {product.id: product for product in Product.query.all()}
    
    # 准备导出数据
    behavior_data = []
    for behavior in user_behaviors:
        user = users.get(behavior.user_id)
        product = products.get(behavior.product_id)
        
        behavior_data.append({
            'id': behavior.id,
            'user_id': behavior.user_id,
            'username': user.username if user else '未知用户',
            'product_id': behavior.product_id,
            'product_name': product.name if product else '未知商品',
            'behavior_type': behavior.behavior_type,
            'created_at': behavior.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': behavior.duration,
            'is_recommended': behavior.is_recommended
        })
    
    # 创建JSON文件
    json_data = json.dumps(behavior_data, ensure_ascii=False, indent=2)
    buffer = io.BytesIO()
    buffer.write(json_data.encode('utf-8'))
    buffer.seek(0)
    
    # 生成文件名
    filename = f"user_behaviors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/json'
    )

@admin.route('/product/<int:id>/edit')
@login_required
@admin_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    return render_template('admin/edit_product.html', product=product) 