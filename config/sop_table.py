from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from config.database import Base

class SOPTable(Base):
    __tablename__ = "sop_table"

    id = Column(Integer, primary_key=True, index=True)
    source_document = Column(String(255), nullable=False, index=True)
    text_content = Column(Text, nullable=False)
    embedding = Column(Vector(2048), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
