from sqlmodel import Relationship

# 使用字符串引用，避免直接导入类导致循环
category_transaction_relationship = Relationship(
    model="Category",  # 使用 model 关键字参数
    back_populates="transactions",
    sa_relationship_kwargs={"lazy": "selectin"}
)

transaction_category_relationship = Relationship(
    model="Transaction",  # 使用 model 关键字参数
    back_populates="category",
    sa_relationship_kwargs={"lazy": "selectin"}
)