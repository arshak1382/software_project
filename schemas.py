from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

# ============================================
# Schema برای UserRoleEnum (هماهنگ با مدل)
# ============================================
class UserRoleEnumSchema(str, Enum):
    VIOWER = "VIOWER"
    EDITOR = "EDITOR"
    ADMIN = "ADMIN"


# ============================================
# 1. Schema های مربوط به Role
# ============================================

# پایه Role - ✅ اصلاح شده (حذف فیلد name)
class RoleBase(BaseModel):
    description: Optional[str] = Field(None, description="توضیحات نقش")
    Role_of_user: UserRoleEnumSchema = Field(default=UserRoleEnumSchema.VIOWER, description="نوع نقش")

# برای ایجاد Role جدید
class RoleCreate(RoleBase):
    pass

# برای به‌روزرسانی Role
class RoleUpdate(BaseModel):
    description: Optional[str] = None
    Role_of_user: Optional[UserRoleEnumSchema] = None

# برای نمایش Role - ✅ اصلاح شده (حذف فیلد name)
class RoleResponse(BaseModel):
    id: int
    Role_of_user: UserRoleEnumSchema
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================
# 2. Schema های مربوط به User
# ============================================

# پایه User
class UserBase(BaseModel):
    username: str = Field(..., max_length=100, description="نام کاربری")
    email: EmailStr = Field(..., description="ایمیل")
    first_name: Optional[str] = Field(None, max_length=100, description="نام")
    last_name: Optional[str] = Field(None, max_length=100, description="نام خانوادگی")

class Userlogin(BaseModel):
    username: str = Field(..., max_length=100, description="نام کاربری")
    password: str = Field(..., min_length=1, description="رمز عبور")

# برای ایجاد User جدید
class UserCreate(UserBase):
    password: str = Field(..., min_length=1, description="رمز عبور")
    role_ids: Optional[List[int]] = Field(default=[], description="لیست شناسه نقش‌ها")

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('رمز عبور باید حداقل 8 کاراکتر باشد')
        return v

# برای به‌روزرسانی User
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    role_ids: Optional[List[int]] = None

    @field_validator('password')
    def validate_password(cls, v):
        if v and len(v) < 8:
            raise ValueError('رمز عبور باید حداقل 8 کاراکتر باشد')
        return v

# برای نمایش User (بدون رمز عبور)
class UserResponse(UserBase):
    id: int
    created_at: datetime
    roles: List[RoleResponse] = []

    model_config = ConfigDict(from_attributes=True)

# برای نمایش User با رمز عبور (برای استفاده داخلی)
class UserInDB(UserResponse):
    password: str


# ============================================
# 3. Schema های مربوط به Author
# ============================================

# پایه Author
class AuthorBase(BaseModel):
    first_name: str = Field(..., max_length=100, description="نام نویسنده")
    last_name: str = Field(..., max_length=100, description="نام خانوادگی نویسنده")
    birth_date: Optional[date] = Field(None, description="تاریخ تولد")
    nationality: Optional[str] = Field(None, max_length=50, description="ملیت")

# برای ایجاد Author جدید
class AuthorCreate(AuthorBase):
    pass

# برای به‌روزرسانی Author
class AuthorUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    birth_date: Optional[date] = None
    nationality: Optional[str] = Field(None, max_length=50)

# برای نمایش Author
class AuthorResponse(AuthorBase):
    id: int
    created_at: datetime
    books: List['BookResponse'] = []

    model_config = ConfigDict(from_attributes=True)


# ============================================
# 4. Schema های مربوط به Book
# ============================================

# پایه Book
class BookBase(BaseModel):
    title: str = Field(..., max_length=200, description="عنوان کتاب")
    publisher: Optional[str] = Field(None, max_length=100, description="ناشر")
    category: Optional[str] = Field(None, max_length=50, description="دسته‌بندی")
    description: Optional[str] = Field(None, description="توضیحات")
    quantity: int = Field(default=1, ge=0, description="تعداد موجودی")

# برای ایجاد Book جدید
class BookCreate(BookBase):
    author_ids: Optional[List[int]] = Field(default=[], description="لیست شناسه نویسندگان")

# برای به‌روزرسانی Book
class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    publisher: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    quantity: Optional[int] = Field(None, ge=0)
    author_ids: Optional[List[int]] = None

# برای نمایش Book
class BookResponse(BookBase):
    id: int
    created_at: datetime
    authors: List[AuthorResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ============================================
# 5. Schema های ترکیبی و کاربردی
# ============================================

# برای نمایش User با نقش‌های کامل
class UserWithRolesResponse(UserResponse):
    roles: List[RoleResponse] = []

# برای نمایش Book با نویسندگان کامل
class BookWithAuthorsResponse(BookResponse):
    authors: List[AuthorResponse] = []

# برای نمایش Author با کتاب‌های کامل
class AuthorWithBooksResponse(AuthorResponse):
    books: List[BookResponse] = []

# برای پاسخ خطا
class ErrorResponse(BaseModel):
    detail: str
    status_code: int

# برای پاسخ موفقیت
class SuccessResponse(BaseModel):
    message: str
    status_code: int = 200


# ============================================
# 6. Schema برای Login
# ============================================

class LoginRequest(BaseModel):
    username: str = Field(..., description="نام کاربری")
    password: str = Field(..., description="رمز عبور")

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============================================
# 7. Schema برای Pagination
# ============================================

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="شماره صفحه")
    per_page: int = Field(default=10, ge=1, le=100, description="تعداد آیتم در هر صفحه")
    sort_by: Optional[str] = Field(None, description="فیلد مرتب‌سازی")
    sort_order: Optional[str] = Field("asc", description="ترتیب مرتب‌سازی (asc/desc)")

class PaginatedResponse(BaseModel):
    total: int = Field(..., description="تعداد کل آیتم‌ها")
    page: int = Field(..., description="شماره صفحه فعلی")
    per_page: int = Field(..., description="تعداد آیتم در هر صفحه")
    total_pages: int = Field(..., description="تعداد کل صفحات")
    items: List = Field(..., description="لیست آیتم‌ها")