from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint
from flask_login import login_required, current_user

from bluelog.extensions import db
from bluelog.forms import SettingForm, PostForm, CategoryForm, LinkForm
from bluelog.models import Post, Category, Comment, Link
from bluelog.utils import redirect_back

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/post/manage')
@login_required
def manage_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['BLUELOG_MANAGE_POST_PER_PAGE'])
    posts = pagination.items
    return render_template('admin/manage_post.html', page=page, pagination=pagination, posts=posts)

@admin_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        # form.category.data的值是category_id
        category = Category.query.get(form.category.data)
        post = Post(title=title, body=body, category=category)
        db.session.add(post)
        db.session.commit()
        flash('Post created.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    return render_template('admin/new_post.html', form=form)

@admin_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category = Category.query.get(form.category.data)
        db.session.commit()
        flash('Post updated.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id
    return render_template('admin/edit_post.html', form=form)

@admin_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect_back()

@admin_bp.route('/post/<int:post_id>/set_comment', methods=['POST'])
@login_required
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if post.can_comment:
        post.can_comment = False
        flash('Comment disabled.', 'success')
    else:
        post.can_comment = True
        flash('Comment enabled.', 'success')
    db.session.commit()
    return redirect_back()