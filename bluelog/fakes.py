import random
from faker import Faker
from sqlalchemy.exc import IntegrityError
from bluelog.extensions import db
from bluelog.models import Admin, Category, Post, Comment, Link

fake = Faker()

def fake_admin():
    admin = Admin(
        username = 'admin',
        blog_title = 'Bluglog',
        blog_sub_title = 'No, I\'m the real thing',
        name = 'Mima Kirigoe',
        about = 'Um, l, Mima Kirigoe, had a fun time as a member of CHAM...'
    )
    admin.set_password('helloflask')
    db.session.add(admin)
    db.session.commit()

def fake_categories(count = 10):
    category = Category(name='Default') # 首先生成一个默认文章分类
    db.session.add(category)

    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        # 分类名称不能重复
        try:
            db.session.commit()
        # 如果名称重复，会抛出sqlalchemy.exc.IntegrityError异常
        except IntegrityError:
            db.session.rollback()

def fake_posts(count = 50):
    for i in range(count):
        post = Post(
            title = fake.sentence(),
            body = fake.text(200),
            # 文章分类在1-分类总数之间随机取值
            category = Category.query.get(random.randint(1, Category.query.count())),
            timestamp = fake.date_time_this_year()
        )
        db.session.add(post)
    db.session.commit()

def fake_comments(count = 500):
    for i in range(count):
        comment = Comment(
            author = fake.name(),
            email =fake.email(),
            site = fake.url(),
            body = fake.sentence(),
            timestamp = fake.date_time_this_year(),
            reviewed = True,
            post = Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    salt = int(count * 0.1)

    for i in range(salt):
        # 未审核的评论
        comment = Comment(
            author = fake.name(),
            email = fake.email(),
            site = fake.url(),
            body = fake.sentence(),
            timestamp = fake.date_time_this_year(),
            reviewed = False,
            post = Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

        # 管理员发表的评论
        comment = Comment(
            author = fake.name(),
            email = fake.email(),
            site = fake.url(),
            body = fake.sentence(),
            timestamp = fake.date_time_this_year(),
            from_admin = True,
            reviewed = True,
            post = Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()

    for i in range(salt):
        # 回复
        comment = Comment(
            author = fake.name(),
            email = fake.email(),
            site = fake.url(),
            body = fake.sentence(),
            timestamp = fake.date_time_this_year(),
            reviewed = True,
            replied = Comment.query.get(random.randint(1, Comment.query.count())),
            post = Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()

def fake_links():
    twitter = Link(name='Twitter', url='#')
    facebook = Link(name='Facebook', url='#')
    linkedin = Link(name='LinkedIn', url='#')
    google = Link(name='Google+', url='#')
    db.session.add([twitter, facebook, linkedin, google])
    db.session.commit()