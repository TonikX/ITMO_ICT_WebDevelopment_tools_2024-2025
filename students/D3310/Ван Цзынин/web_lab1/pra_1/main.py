from fastapi import FastAPI, HTTPException
from .models import Profession, Skill, Warrior, BlogArticle, BlogComment
# 创建 FastAPI 应用实例
app = FastAPI(
    title="WebLab1 API",
    description="实践任务：基于 FastAPI 实现战士、职业、博客相关接口",
    version="1.0.0"
)

# 模拟数据库（替代之前的临时数据 ）
# 战士数据
warriors_db = [
    Warrior(
        id=1,
        race="director",
        name="Мартынов Дмитрий",
        level=12,
        profession=Profession(id=1, title="Влиятельный человек", description="Эксперт по всем вопросам"),
        skills=[
            Skill(id=1, name="Купле-продажа компрессоров", description=""),
            Skill(id=2, name="Оценка имущества", description="")
        ]
    ),
    Warrior(
        id=2,
        race="worker",
        name="Андрей Косякин",
        level=12,
        profession=Profession(id=1, title="Дельфист-гребец", description="Уважаемый сотрудник"),
        skills=[]
    )
]

# 职业数据
professions_db = [
    Profession(id=1, title="Влиятельный человек", description="Эксперт по всем вопросам"),
    Profession(id=2, title="Дельфист-гребец", description="Уважаемый сотрудник")
]

# 博客文章数据
blog_articles_db = [
    BlogArticle(
        id=1,
        title="第一篇博客文章",
        author="张三",
        comments=[
            BlogComment(id=1, content="很棒的文章！", author="李四"),
            BlogComment(id=2, content="期待更多！", author="王五")
        ]
    ),
    BlogArticle(
        id=2,
        title="第二篇博客文章",
        author="赵六",
        comments=[]
    )
]


# -------------- 战士相关接口 --------------
@app.get("/warriors_list", response_model=list[Warrior], summary="获取所有战士列表")
async def get_warriors():
    """
    获取所有战士的完整信息，包括职业、技能等。
    """
    return warriors_db


@app.get("/warrior/{warrior_id}", response_model=Warrior, summary="获取单个战士信息")
async def get_warrior(warrior_id: int):
    """
    根据战士 ID 获取具体信息。
    - 如果战士不存在，返回 404 错误。
    """
    for warrior in warriors_db:
        if warrior.id == warrior_id:
            return warrior
    raise HTTPException(status_code=404, detail="Warrior not found")


@app.post("/warrior", response_model=Warrior, summary="创建新战士")
async def create_warrior(warrior: Warrior):
    """
    创建新的战士记录：
    - 接收 Warrior 模型数据，自动校验字段。
    - 添加到模拟数据库并返回创建结果。
    """
    warriors_db.append(warrior)
    return warrior


@app.delete("/warrior/delete/{warrior_id}", summary="删除战士")
async def delete_warrior(warrior_id: int):
    """
    根据 ID 删除战士：
    - 找到对应战士则删除，返回成功消息。
    - 未找到则返回 404 错误。
    """
    for i, warrior in enumerate(warriors_db):
        if warrior.id == warrior_id:
            del warriors_db[i]
            return {"status": 200, "message": "Warrior deleted"}
    raise HTTPException(status_code=404, detail="Warrior not found")


@app.put("/warrior/{warrior_id}", response_model=list[Warrior], summary="更新战士信息")
async def update_warrior(warrior_id: int, updated_warrior: Warrior):
    """
    根据 ID 更新战士信息：
    - 找到对应战士则替换为新数据。
    - 未找到则返回 404 错误。
    """
    for i, warrior in enumerate(warriors_db):
        if warrior.id == warrior_id:
            warriors_db[i] = updated_warrior
            return warriors_db
    raise HTTPException(status_code=404, detail="Warrior not found")


# -------------- 职业相关接口 --------------
@app.get("/professions_list", response_model=list[Profession], summary="获取所有职业列表")
async def get_professions():
    return professions_db


@app.get("/profession/{profession_id}", response_model=Profession, summary="获取单个职业信息")
async def get_profession(profession_id: int):
    for profession in professions_db:
        if profession.id == profession_id:
            return profession
    raise HTTPException(status_code=404, detail="Profession not found")


# -------------- 博客文章相关接口 --------------
@app.get("/articles_list", response_model=list[BlogArticle], summary="获取所有博客文章列表")
async def get_articles():
    return blog_articles_db


@app.get("/article/{article_id}", response_model=BlogArticle, summary="获取单个博客文章信息")
async def get_article(article_id: int):
    for article in blog_articles_db:
        if article.id == article_id:
            return article
    raise HTTPException(status_code=404, detail="Article not found")


@app.post("/article", response_model=BlogArticle, summary="创建新博客文章")
async def create_article(article: BlogArticle):
    blog_articles_db.append(article)
    return article


@app.delete("/article/delete/{article_id}", summary="删除博客文章")
async def delete_article(article_id: int):
    for i, article in enumerate(blog_articles_db):
        if article.id == article_id:
            del blog_articles_db[i]
            return {"status": 200, "message": "Article deleted"}
    raise HTTPException(status_code=404, detail="Article not found")


@app.put("/article/{article_id}", response_model=list[BlogArticle], summary="更新博客文章信息")
async def update_article(article_id: int, updated_article: BlogArticle):
    for i, article in enumerate(blog_articles_db):
        if article.id == article_id:
            blog_articles_db[i] = updated_article
            return blog_articles_db
    raise HTTPException(status_code=404, detail="Article not found")


@app.get("/article/{article_id}/comments", response_model=list[BlogComment], summary="获取文章评论列表")
async def get_article_comments(article_id: int):
    for article in blog_articles_db:
        if article.id == article_id:
            return article.comments
    raise HTTPException(status_code=404, detail="Article not found")


@app.post("/article/{article_id}/comment", response_model=BlogArticle, summary="为文章添加评论")
async def add_article_comment(article_id: int, comment: BlogComment):
    for article in blog_articles_db:
        if article.id == article_id:
            article.comments.append(comment)
            return article
    raise HTTPException(status_code=404, detail="Article not found")