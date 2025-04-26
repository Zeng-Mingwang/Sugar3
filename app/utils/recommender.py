import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.models.models import Product, UserBehavior
from app import db
from flask_login import current_user

class Recommender:
    def __init__(self):
        self.products = None
        self.user_product_matrix = None
        self.similarity_matrix = None
        # 不在初始化时加载数据
        # self._load_data()

    def _load_data(self):
        # 加载所有产品
        self.products = Product.query.all()
        
        # 创建用户-产品交互矩阵
        behaviors = UserBehavior.query.all()
        
        # 如果没有用户行为数据，则返回
        if not behaviors or not self.products:
            return
            
        user_ids = set(b.user_id for b in behaviors)
        product_ids = set(p.id for p in self.products)
        
        # 如果没有用户或产品，则返回
        if not user_ids or not product_ids:
            return
            
        self.user_product_matrix = np.zeros((len(user_ids), len(product_ids)))
        
        # 填充交互矩阵
        for behavior in behaviors:
            user_idx = list(user_ids).index(behavior.user_id)
            product_idx = list(product_ids).index(behavior.product_id)
            if behavior.behavior_type == 'view':
                self.user_product_matrix[user_idx, product_idx] = 1
            elif behavior.behavior_type == 'click':
                self.user_product_matrix[user_idx, product_idx] = 2
            elif behavior.behavior_type == 'purchase':
                self.user_product_matrix[user_idx, product_idx] = 3

        # 计算产品相似度矩阵
        self.similarity_matrix = cosine_similarity(self.user_product_matrix.T)

    def get_recommendations(self, product_id, n_recommendations=4):
        if self.similarity_matrix is None:
            self._load_data()
            
        # 如果没有数据，返回空列表
        if self.products is None or len(self.products) == 0:
            return []
        
        # 获取当前用户已查看过的商品ID列表
        viewed_product_ids = []
        if current_user.is_authenticated:
            viewed_behaviors = UserBehavior.query.filter_by(
                user_id=current_user.id,
                behavior_type='view'
            ).all()
            viewed_product_ids = [b.product_id for b in viewed_behaviors]
            
        # 随机选择推荐产品（初始阶段没有用户行为数据时使用）
        if self.similarity_matrix is None:
            import random
            # 排除当前商品和用户已查看过的商品
            available_products = [p for p in self.products if p.id != product_id and p.id not in viewed_product_ids]
            if len(available_products) == 0:
                return []
            # 随机选择并打乱推荐产品
            recommended_products = random.sample(available_products, min(n_recommendations, len(available_products)))
            random.shuffle(recommended_products)
            return recommended_products
        
        try:
            product_idx = list(p.id for p in self.products).index(product_id)
            similar_scores = self.similarity_matrix[product_idx]
            
            # 获取最相似的产品索引
            similar_indices = similar_scores.argsort()[::-1][1:]
            
            # 返回推荐产品，排除当前商品和用户已查看过的商品
            recommended_products = []
            for idx in similar_indices:
                product = self.products[idx]
                if product.id != product_id and product.id not in viewed_product_ids:
                    recommended_products.append(product)
                    if len(recommended_products) >= n_recommendations:
                        break
                
            # 随机打乱推荐产品顺序
            import random
            random.shuffle(recommended_products)
            return recommended_products
        except (ValueError, IndexError):
            # 如果出现错误（如产品ID不存在），也返回随机推荐
            import random
            # 排除当前商品和用户已查看过的商品
            available_products = [p for p in self.products if p.id != product_id and p.id not in viewed_product_ids]
            if len(available_products) == 0:
                return []
            # 随机选择并打乱推荐产品
            recommended_products = random.sample(available_products, min(n_recommendations, len(available_products)))
            random.shuffle(recommended_products)
            return recommended_products 