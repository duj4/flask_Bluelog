# 一共五张表：Admin, Category, Post, Comment和Link

from datetime import datetime
from flask_login import UserMixin
from bluelog.extensions import db

from werkzeug.security import generate_password_hash, check_password_hash

# 管理员
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128)) # 密码散列值
    blog_title = db.Column(db.String(60))
    blog_sub_title = db.Column(db.String(100))
    name = db.Column(db.String(30))
    about = db.Column(db.Text)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

# 分类
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True) # 分类名称不允许重复

    # 和Post的双向关系
    posts = db.relationship('Post', back_populates='category')

# 文章
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # 和Category的双向关系
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', back_populates='posts')

    # 和Comment的双向关系
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan') # 设置级联删除，即文章删除之后对应的评论也一并删除

# 评论
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30))
    email = db.Column(db.String(254))
    site = db.Column(db.String(255))
    body = db.Column(db.Text)
    from_admin = db.Column(db.Boolean, default=False) # 是否是管理员的评论
    reviewed = db.Column(db.Boolean, default=False) # 是否通过审核，以防止垃圾评论或不当评论
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 和Post的双向关系
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='comments')

    # 评论回复功能，并在获取某个评论时可以通过关系属性获得对应的回复，这样就可以在模板中显示出评论之间的对应关系
    # 因为回复本身也是评论，如果在评论模型内建立层级关系，就可以在一个模型中表示评论和评论的回复
    # 这种在同一个模型内部的一对多关系在SQLAlchemy中被称为邻接列表关系(Adjacency List Relationship)
    # 在Comment模型内部添加一个外键指向它自身，这样就得到一种层级关系：每个评论对象都可以包含多个自评论，即回复
    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan') # 设置级联删除，即评论删除之后对应的回复也一并删除
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])

# 添加链接
class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    url = db.Column(db.String(255))