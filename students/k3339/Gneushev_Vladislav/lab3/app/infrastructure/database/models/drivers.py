from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from app.infrastructure.database.models.base import Base


class DriverClassDB(Base):
    __tablename__ = 'driver_classes'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)

    drivers = relationship('DriverDB', back_populates='driver_class')


class DriverSalaryDB(Base):
    __tablename__ = 'driver_salaries'
    id = Column(Integer, primary_key=True)
    work_experience_over_months = Column(Integer, nullable=False)
    driver_class_id = Column(
        Integer,
        ForeignKey(
            "driver_classes.id",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        nullable=False
    )
    salary_rub = Column(Integer, nullable=False)

    driver_class: Mapped[DriverClassDB] = relationship('DriverClassDB', lazy='joined')


class DriverDB(Base):
    __tablename__ = 'drivers'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(32), nullable=False)
    last_name = Column(String(32), nullable=False)
    passport_info = Column(String(10), nullable=False)
    driver_class_id = Column(
        Integer,
        ForeignKey(
            "driver_classes.id",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        nullable=False
    )
    work_experience_months = Column(Integer, nullable=False)

    driver_class: Mapped[DriverClassDB] = relationship('DriverClassDB', back_populates='drivers', lazy='joined')
    assignments = relationship('DriverAssignmentDB', back_populates='driver', lazy='joined')
