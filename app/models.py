from .database import Base 
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, ARRAY
from sqlalchemy.sql.sqltypes import TIMESTAMP 
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    rollno = Column(String, nullable=False)
    name=Column(String, nullable=False, unique=True)
    password=Column(String, nullable=False)
    department=Column(String, nullable=False)
    created_at=Column(TIMESTAMP, server_default=text('now()'), nullable=False)
    questions = relationship(
        "Question",
        back_populates="owner",
        cascade="all, delete"
    )

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, nullable=False)
    question = Column(String, nullable=False)
    tags = Column(
        ARRAY(String),
        nullable=False
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    isSolved = Column(
        Boolean,
        nullable=False,
        server_default='FALSE'
    )
    
    owner = relationship(
        "User",
        back_populates="questions"
    )

class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, nullable=False)

    answer = Column(
        String,
        nullable=False
    )

    question_id = Column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    owner = relationship("User")

class Vote(Base):
    __tablename__ = "votes"

    answer_id = Column(
        Integer,
        ForeignKey("answers.id", ondelete="CASCADE"),
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    vote_dir = Column(Integer, nullable=False)   # 1 or -1

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False
    )

class Follow(Base):
    __tablename__ = "follows"

    requester_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    receiver_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    status = Column(
        String,
        nullable=False
    )   # pending, accepted

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False
    )

    requester = relationship(
        "User",
        foreign_keys=[requester_id]
    )

    receiver = relationship(
        "User",
        foreign_keys=[receiver_id]
    )
