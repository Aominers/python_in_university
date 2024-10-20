class Book:
    def __init__(self, id, title, author, publication_year,quantity):
        self.id = id
        self.title = title
        self.author = author
        self.publication_year = publication_year
        self.quantity = quantity

    def __str__(self):
        return (f"图书ID: {self.id}, 名称: {self.title}, "
                f"作者: {self.author}, 出版日期: {self.publication_year}, "
                f" 数量: {self.quantity}")