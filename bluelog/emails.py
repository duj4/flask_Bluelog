from threading import Thread
from flask import url_for, current_app
from flask_mail import Message
from bluelog.extensions import mail

def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)

def send_email(subject, to, html):
    # 程序实例时通过工厂函数构建，所以实例化Thread类时，使用代理对象current_app作为args参数列表中app的值
    # 因为在新建的线程时需要真正的程序对象来创建上下文，所以不能直接传入current_app，而是传入对current_app调用_get_current_object()方法来获取到的被代理的程序实例
    app = current_app._get_current_object()
    message = Message(subject, recipients=[to], html=html)
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr

def send_new_comment_email(post):
    post_url = url_for('blog.show_post', post_id=post.id, _external=True) + '#comments'
    send_email(subject='New comment', to=current_app.config['BLUELOG_ADMIN_EMAIL'],
               html='<p>New comment in post<i>%s</i>, click the link below to check:</p>'
                    '<p><a href="%s">%s</a></p>'
                    '<p><small style="color: #868e96">Do not reply this email.</small></p>'
                    % (post.title, post_url, post_url))

def send_new_reply_email(comment):
    post_url = url_for('blog.show_post', post_id=comment.post_id, _external=True) + '#comment'
    send_email(subject='New reply', to=comment.email,
               html='<p>New reply for the comment you left in post <i>%s</i>, click the link below to check: </p>'
                    '<p><a href="%s">%s</a></p>'
                    '<p><small style="color: #868e96">Do not reply this email.</small></p>'
                    % (comment.post.title, post_url, post_url))