from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.models.models import Product, CartItem, UserBehavior
from app.utils.recommender import Recommender
from app import db
from datetime import datetime

bp = Blueprint('main', __name__)
# 不在模块级别初始化推荐系统
# recommender = Recommender()

@bp.route('/')
def index():
    products = Product.query.limit(20).all()
    return render_template('index.html', products=products)

@bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    is_recommend = request.args.get('is_recommend', 'false').lower() == 'true'
    
    # 在路由函数内初始化推荐系统
    recommender = Recommender()
    # 获取推荐产品
    recommended_products = recommender.get_recommendations(product_id)
    
    # 记录用户浏览行为
    if current_user.is_authenticated:
        # 获取推荐产品的ID列表
        recommended_ids = [str(p.id) for p in recommended_products]
        recommended_ids_str = ','.join(recommended_ids)
        
        behavior = UserBehavior(
            user_id=current_user.id,
            product_id=product_id,
            behavior_type='view',
            created_at=datetime.utcnow(),
            is_recommended=is_recommend,
            recommended_product_ids=recommended_ids_str
        )
        db.session.add(behavior)
        db.session.commit()
    
    return render_template('product_detail.html', 
                         product=product, 
                         recommended_products=recommended_products,
                         is_recommend=is_recommend)

@bp.route('/cart')
@login_required
def cart():
    # 只显示未购买的购物车项
    cart_items = CartItem.query.filter_by(user_id=current_user.id, is_purchased=False).all()
    # 计算总价
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@bp.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    is_recommended = request.form.get('is_recommended', 'false').lower() == 'true'
    
    # 检查商品是否已在购物车中
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id,
        is_purchased=False
    ).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity,
            is_purchased=False,
        )
        db.session.add(cart_item)
    
    behavior = UserBehavior(
        user_id=current_user.id,
        product_id=product_id,
        behavior_type='click',
        is_recommended=is_recommended,
        created_at=datetime.utcnow()
    )
    db.session.add(behavior)
    
    db.session.commit()
    return jsonify({'status': 'success'})

@bp.route('/update_cart', methods=['POST'])
@login_required
def update_cart():
    item_id = request.form.get('item_id')
    quantity = int(request.form.get('quantity', 1))
    
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != current_user.id:
        return jsonify({'status': 'error', 'message': '无权限操作'}), 403
    
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity
    
    db.session.commit()
    return jsonify({'status': 'success'})

@bp.route('/track_behavior', methods=['POST'])
@login_required
def track_behavior():
    data = request.json
    behavior = UserBehavior(
        user_id=current_user.id,
        product_id=data['product_id'],
        behavior_type=data['behavior_type'],
        duration=data.get('duration'),
        is_recommended=data.get('is_recommended', False),
        created_at=datetime.utcnow()
    )
    db.session.add(behavior)
    db.session.commit()
    return jsonify({'status': 'success'})

@bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    # 获取用户的购物车商品
    cart_items = CartItem.query.filter_by(user_id=current_user.id, is_purchased=False).all()
    
    if not cart_items:
        return jsonify({'status': 'error', 'message': '购物车为空'}), 400
    
    try:
        # 记录购买行为
        for item in cart_items:
            add_behavior_list = UserBehavior.query.filter_by(
                user_id=current_user.id,
                product_id=item.product_id,
                behavior_type='click',
            ).all()
            
            for behavior in add_behavior_list:
                purchase_behavior = UserBehavior(
                    user_id=current_user.id,
                    product_id=item.product_id,
                    behavior_type='purchase',
                    created_at=datetime.utcnow(),
                    is_recommended=behavior.is_recommended
                )
                db.session.add(purchase_behavior)
            
            # 将购物车项标记为已购买，而不是删除
            item.is_purchased = True
        
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500 