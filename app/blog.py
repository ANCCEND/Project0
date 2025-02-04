from flask import Blueprint, request, jsonify
from .models import User, Post
from .extensions import db
from .tools import response_template
from sqlalchemy.exc import IntegrityError
from datetime import timedelta, datetime, timezone
from .tools import response_template
from sqlalchemy import func

blog = Blueprint("blog", __name__, url_prefix="/")


@blog.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.Date.desc()).paginate(
        page=page, per_page=10, error_out=False, max_per_page=100
    )

    post_data = [
        {
            "user": post.author.Username,
            "time": post.Date.strftime("%Y-%m-%d %H:%M:%S"),
            "title": post.Title,
            "category": post.Category,
            "content": post.Content,
        }
        for post in posts.items
    ]

    pagination_info = {
        "page": posts.page,
        "per_page": posts.per_page,
        "total": posts.total,
        "pages": posts.pages,
        "has_next": posts.has_next,
        "has_prev": posts.has_prev,
        "next_page": posts.next_num if posts.has_next else None,
        "prev_page": posts.prev_num if posts.has_prev else None,
    }
    return response_template(
        True, "show success", {"posts": post_data, "pagination": pagination_info}
    )


@blog.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        user = request.form.get("username")
        title = request.form.get("title")
        category = request.form.get("category")
        content = request.form.get("content")
        time = datetime.now()

        user_obj = User.query.filter_by(Username=user).first()
        if user and title and category and content:
            new_post = Post(
                author=user_obj,
                Title=title,
                Category=category,
                Content=content,
                Date=time,
            )
            db.session.add(new_post)
            db.session.commit()
            return response_template(
                True,
                "Publish successful",
                {
                    "id": new_post.id,
                    "author": new_post.author.Username,  # 获取作者用户名
                    "title": new_post.Title,
                    "category": new_post.Category,
                    "content": new_post.Content,
                    "date": new_post.Date.strftime("%Y-%m-%d %H:%M:%S"),  # 格式化时间
                },
            )
        else:
            error = "Please enter complete information"
            return response_template(False, error, status_code=401)
    return response_template(False, status_code=500)


@blog.route("/search")
def search():
    query = request.args.get("q")
    user = request.args.get("user")
    category = request.args.get("category")
    sort = request.args.get("sort_by")
    page = request.args.get("page", 1, type=int)
    per_page = 8

    if category:
        if query:
            results = Post.query.filter(
                (Post.Title.contains(query))
                | (Post.Content.contains(query)) & (Post.Category == category)
            )
        if user:
            user_obj = User.query.filter_by(Username=user).first()
            results = Post.query.filter(
                (Post.author == user_obj) & (Post.Category == category)
            )

        if sort == "length":
            results = results.order_by(func.length(Post.Content).desc())
        else:
            results = results.order_by(Post.Date.desc())
    else:
        if query:
            results = Post.query.filter(
                (Post.Title.contains(query)) | (Post.Content.contains(query))
            )
        if user:
            user_obj = User.query.filter_by(Username=user).first()
            results = Post.query.filter(Post.author == user_obj)

        if sort == "length":
            results = results.order_by(func.length(Post.Content).desc())
        else:
            results = results.order_by(Post.Date.desc())

    paginated_posts = results.paginate(page=page, per_page=per_page)

    results_data = [
        {
            "user": post.author.Username,
            "time": post.Date.strftime("%Y-%m-%d %H:%M:%S"),
            "title": post.Title,
            "category": post.Category,
            "content": post.Content,
        }
        for post in paginated_posts.items
    ]
    
    pagination_info = {
        "page": paginated_posts.page,
        "per_page": paginated_posts.per_page,
        "total": paginated_posts.total,
        "pages": paginated_posts.pages,
        "has_next": paginated_posts.has_next,
        "has_prev": paginated_posts.has_prev,
        "next_page": paginated_posts.next_num if paginated_posts.has_next else None,
        "prev_page": paginated_posts.prev_num if paginated_posts.has_prev else None,
    }

    return response_template(
        True,
        "Results",
        {"posts": results_data, "pagination": pagination_info}
    )
