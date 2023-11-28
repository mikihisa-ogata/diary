from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import (
    StringField,
    SubmitField,
    ValidationError,
    TextAreaField,
    SelectField,
)
from wtforms.validators import DataRequired, Email
from diary.models import BlogCategory
from flask_wtf.file import FileField, FileAllowed

# クラスは全部で5つ
# BlogCategoryForm
# UpdateCategoryForm
# BlogPostForm
# BlogSearchForm


class BlogCategryForm(FlaskForm):
    category = StringField("カテゴリ名", validators=[DataRequired()])
    submit = SubmitField("保存")

    def validate_category(self, field):
        if BlogCategory.query.filter_by(category=field.data).first():
            raise ValidationError("入力されたカテゴリ名はすでに使われています")


class UpdateCategoryForm(FlaskForm):
    category = StringField("カテゴリ名", validators=[DataRequired()])
    submit = SubmitField("更新")

    def __init__(
        self, blog_category_id, *args, **kwargs
    ):  # 継承もとの初期設定を上書きしないようにsuperを使う
        super(UpdateCategoryForm, self).__init__(*args, **kwargs)
        self.id = blog_category_id

    def validate_category(self, field):
        if BlogCategory.query.filter_by(
            category=field.data
        ).first():  # 入力されたフォームがすでに格納されているcategoryに存在しないかの確認
            raise ValidationError("入力されたカテゴリ名はすでに使われています。")


class BlogPostForm(FlaskForm):
    title = StringField("タイトル", validators=[DataRequired()])
    category = SelectField("カテゴリ", coerce=int)
    summary = StringField("要約", validators=[DataRequired()])
    text = TextAreaField("本文", validators=[DataRequired()])
    picture = StringField("アイキャッチ画像", validators=[FileAllowed(["jpg", "png"])])
    submit = SubmitField("投稿")

    def _set_category(self):  # メソッドの前の_ 内部用
        blog_categories = BlogCategory.query.all()
        self.category.choices = [
            (blog_category.id, blog_category.category)
            for blog_category in blog_categories
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 継承元の初期処理を残しつつ、新たな初期処理を追記
        self._set_category()


class BlogSearchForm(FlaskForm):
    searchtext = StringField("検索テキスト", validators=[DataRequired()])
    submit = SubmitField("検索")
