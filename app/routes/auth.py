from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.models import User
from app import db
import logging

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('用户名已存在')
            return redirect(url_for('auth.register'))
        
        new_user = User(
            username=username,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('用户名或密码错误')
            return redirect(url_for('auth.login'))
        
        current_app.logger.info(f'用户 {username} 登录成功')
        current_app.logger.info(f'Session 配置: SECURE={current_app.config["SESSION_COOKIE_SECURE"]}, '
                              f'HTTPONLY={current_app.config["SESSION_COOKIE_HTTPONLY"]}, '
                              f'SAMESITE={current_app.config["SESSION_COOKIE_SAMESITE"]}')
        
        login_user(user, remember=True)
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index')) 