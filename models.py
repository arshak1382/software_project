from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
import bcrypt

# ============================================
# تعریف Enum برای نقش‌های کاربری
# ============================================
class UserRoleEnum(enum.Enum):
    VIOWER = "VIOWER"
    EDITOR = "EDITOR"
    ADMIN = "ADMIN"

# ✅ این خط را درست کنید - مقدار deprecated باید "auto" باشد

# ============================================
# جدول واسط Many-to-Many بین کتاب و نویسنده
# ============================================
book_author = Table(
    'book_author',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id'), primary_key=True),
    Column('author_id', Integer, ForeignKey('authors.id'), primary_key=True)
)

# ============================================
# جدول واسط Many-to-Many بین کاربر و نقش
# ============================================
user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)


# ============================================
# 1. جدول نقش‌های کاربری (Role)
# ============================================
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    Role_of_user = Column(Enum(UserRoleEnum), nullable=False, default="VIOWER")

    # رابطه Many-to-Many با کاربران
    users = relationship("User", secondary=user_role, back_populates="roles")


# ============================================
# 2. جدول کاربران (User) - این کلاس را اضافه کنید
# ============================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    roles = relationship("Role", secondary=user_role, back_populates="users")

    def hash_password(self, password: str) -> str:
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def verify_password(self, plain_password: str) -> bool:
        try:
            plain_bytes = plain_password.encode('utf-8')
            if len(plain_bytes) > 72:
                plain_bytes = plain_bytes[:72]
            return bcrypt.checkpw(plain_bytes, self.password.encode('utf-8'))
        except:
            return False
    def set_password(self, password: str) -> None:
        """تنظیم پسورد هش شده"""
        self.password = self.hash_password(password)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

# ============================================
# 3. جدول نویسندگان (Author)
# ============================================
class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=True)
    nationality = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # رابطه Many-to-Many با کتاب‌ها
    books = relationship("Book", secondary=book_author, back_populates="authors")


# ============================================
# 4. جدول کتاب‌ها (Book)
# ============================================
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    publisher = Column(String(100), nullable=True)
    category = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # رابطه Many-to-Many با نویسندگان
    authors = relationship("Author", secondary=book_author, back_populates="books")