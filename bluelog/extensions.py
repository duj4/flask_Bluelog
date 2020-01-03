# 初始化扩展
# 为了完成扩展的初始化操作，需要在实例化扩展类时传入程序实例。但使用工厂函数时，并没有一个创建好的程序实例可以导入。如果把实例化操作放到工厂函数钟，那么就没有一个全局的扩展对象可以使用
# 为了解决这个问题，大部分扩展都提供了一个init_app()方法来支持分离扩展的实例化和初始化操作
# 将扩展类实例化的工作集中放到extensions.py中

from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
ckeditor = CKEditor()
mail = Mail()
moment = Moment()
toolbar = DebugToolbarExtension()
migrate = Migrate()