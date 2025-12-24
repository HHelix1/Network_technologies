from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Enum, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, sessionmaker, relationship
from datetime import date, datetime
from enum import Enum as PyEnum
from typing import List, Optional

DATABASE_URL = "sqlite:///./training_system.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class AccessRights(str, PyEnum):
    ADMIN = "admin"
    HR = "hr"
    MANAGER = "manager"
    EMPLOYEE = "employee"

class TrainingStatus(str, PyEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class EducationalProgram(Base):
    __tablename__ = "educational_programs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    protocol_number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[date] = mapped_column(Date, default=date.today)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    training_assignments: Mapped[List["TrainingAssignment"]] = relationship(
        back_populates="educational_program", cascade="all, delete-orphan"
    )

class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20))
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    hire_date: Mapped[date] = mapped_column(Date, default=date.today)
    training_assignments: Mapped[List["TrainingAssignment"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )
    user: Mapped[Optional["User"]] = relationship(back_populates="employee", uselist=False)

class TrainingAssignment(Base):
    __tablename__ = "training_assignments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    education_id: Mapped[int] = mapped_column(ForeignKey("educational_programs.id"))
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[TrainingStatus] = mapped_column(Enum(TrainingStatus), default=TrainingStatus.PLANNED)
    updated_at: Mapped[date] = mapped_column(Date, default=date.today)
    employee: Mapped["Employee"] = relationship(back_populates="training_assignments")
    educational_program: Mapped["EducationalProgram"] = relationship(back_populates="training_assignments")

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    access_rights: Mapped[AccessRights] = mapped_column(Enum(AccessRights), default=AccessRights.EMPLOYEE)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    employee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"))
    employee: Mapped[Optional["Employee"]] = relationship(back_populates="user")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()