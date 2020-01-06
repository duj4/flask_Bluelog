from flask import render_template, Blueprint, request, current_app, url_for, flash, redirect
from bluelog.models import Post, Category, Comment
from bluelog.forms import AdminCommentForm, CommentForm
from bluelog.emails import send_new_comment_email, send_new_reply_email
from bluelog.extensions import db

blog_bp = Blueprint('blog', __name__)

@blog_bp.route('/')
def index():
    # 分页显示文章列表
    # 从查询字符串获取当前页数
    page = request.args.get('page', 1, type=int)
    # 每页数量
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    # 分页对象
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    # 当前页数的记录列表
    posts = pagination.items
    return render_template('blog/index.html', pagination=pagination, posts=posts)

@blog_bp.route('/about')
def about():
    return render_template('blog/about.html')

@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    # 分类文章列表
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    # with_parent()查询方法会返回查询对象，所以可以继续附加其他查询方法来过滤文章记录
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/category.html', category=category, pagination=pagination, posts=posts)

@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_COMMENT_PER_PAGE']
    # 通过文章获取相应的评论
    pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.asc()).paginate(page, per_page=per_page)
    comments = pagination.items

    # 发表评论
    # 如果当前用户通过验证
    if current_user.is_authenticated:
        # 实例化AdminCommentForm类，并对三个隐藏字段赋予相应的值
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config['BLUELOG_EMAIL']
        form.site.data = url_for('.index')
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False

    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        comment = Comment(
            author=author, email=email, site=site, body=body, from_admin=from_admin, post=post, reviewed=reviewed
        )
        replied_id = request.args.get('reply')
        # 如果请求URL的查询字符串中是否包含replied_id的值，如果包含，则表示提交的评论时一条回复
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
            send_new_reply_email(replied_comment)
        db.session.add(comment)
        db.session.commit()

        if current_user.is_authenticated:
            flash('Comment published', 'success')
        else:
            flash('Thanks, your comment will be published after reviewed.', 'info')
            send_new_comment_email(post)
        return redirect(url_for('.show_post', post_id=post_id))
    return render_template('blog/post.html', post=post, pagination=pagination, comments=comments)

@blog_bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment.post.can_comment:
        flash('Comment is disabled.', 'warning')
        return redirect(url_for('.show_post', post_id=comment.post.id))
    return redirect(
        # 当使用url_for()函数构建URL时，任何多余的关键字参数都会被自动转换为插叙字符串，当点击某个评论右侧的回复按钮时，重定向后的页面URL将会是:
        # http://localhost:5000/post/23?id=4&author=peter#comment-form
        url_for('.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + '#comment-form'
    )