from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float
from config import DATABASE_URL

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    xp = Column(Integer, default=0)
    level = Column(String, default="Beginner")

class Folder(Base):
    __tablename__ = 'folders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String(100), nullable=False)
    
    tests = relationship("TestBank", back_populates="folder", cascade="all, delete-orphan")

class TestBank(Base):
    __tablename__ = 'test_banks'
    id = Column(Integer, primary_key=True)
    folder_id = Column(Integer, ForeignKey('folders.id'))
    title = Column(String(255), nullable=False)
    version = Column(Integer, default=1)
    
    folder = relationship("Folder", back_populates="tests")
    questions = relationship("Question", back_populates="test_bank", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    test_bank_id = Column(Integer, ForeignKey('test_banks.id'))
    question_text = Column(Text, nullable=False)
    options = Column(Text, nullable=False)  # "A) Java B) Python C) C++" formatda yoki JSON string
    correct_option = Column(String(10), nullable=True)  # AI aniqlaguncha yoki foydalanuvchi kiritguncha nullable
    ai_confidence = Column(Float, nullable=True)

    test_bank = relationship("TestBank", back_populates="questions")

# Dvigatelni asinxron ulash
# Agar Railway oddiy postgresql:// bersa, uni +asyncpg rejimiga o'tkazish
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        # Baza jadvallarini yaratish
        await conn.run_sync(Base.metadata.create_all)
      
