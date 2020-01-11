import os
import click
from flask import Flask, render_template, request
from flask_login import current_user
from flask_wtf.csrf import CSRFError

from bluelog.blueprints.admin import admin_bp
from bluelog.blueprints.auth import auth_bp
from bluelog.blueprints.blog import blog_bp
from bluelog.settings import config
from bluelog.extensions import bootstrap, db, csrf, moment, ckeditor, mail, login_manager, moment, toolbar, migrate
from bluelog.fakes import fake_admin, fake_categories, fake_posts, fake_comments, fake_links
from bluelog.models import Admin, Category, Post, Comment, Link

basedir = os.path.abspath(os.path.dirname(os.path.dirname((__file__))))

# 使用工厂函数创建程序实例
def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('bluelog')
    app.config.from_object(config[config_name])

    register_logging(app) # 注册日志处理器
    register_extensions(app) # 注册扩展
    register_blueprints(app) # 注册蓝本
    register_commands(app) # 注册自定义shell命令
    register_shell_context(app) # 注册shell上下文处理函数
    register_template_context(app) # 注册模板上下文处理函数
    # register_request_handlers(app) # 注册请求处理函数
    register_errors(app)  # 注册错误处理函数

    return app

def register_logging(app):
    pass

def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    toolbar.init_app(app)
    migrate.init_app(app)

def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')

def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop')
    def initdb(drop):
        """Initialize the database"""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
    def forge(category, post, comment):
        """Generates the fake categories, posts and comments"""
        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator...')
        fake_admin()

        click.echo('Generating %d categories...' % category)
        fake_categories(category)

        click.echo('Generating %d posts...' % post)
        fake_posts(post)

        click.echo('Generating %d comments...' % comment)
        fake_comments(comment)

        click.echo('Generating links...')
        fake_links()

        click.echo('Done!')

    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password to login.')
    def init(username, password):
        """Building Bluelog, just for you."""
        click.echo('Initializing the database...')
        db.create_all()
        admin = Admin.query.first()

        # 如果数据库中已经有管理员记录就更新用户名和密码
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.username =  username
            admin.set_password(password)
        # 若不存在则直接创建
        else:
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                username=username,
                blog_title='Bluelog',
                blog_sub_title='No, I\'m the real thing.',
                name='Admin',
                about='Anything about you.')
            admin.set_password(password)
            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo('Creating the default category...')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('Done.')

def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, Admin=Admin, Post=Post, Category=Category, Comment=Comment)

def register_template_context(app):
    # 为了避免在每个视图函数中渲染模板时传入重复数据，在这个模板上下文处理函数中向模板上下文添加管理员对象变量
    # 在多个页面中都包含的边栏中包含分类列表，也把分类数据传入到模板上下文中
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.order_by(Link.name).all()

        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None

        return dict(admin=admin, categories=categories, links=links, unread_comments=unread_comments)

def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def bad_request(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def bad_request(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400