# 使 app.models 成为一个包
from app.models.models import User, Product, CartItem, UserBehavior

__all__ = ['User', 'Product', 'CartItem', 'UserBehavior'] 