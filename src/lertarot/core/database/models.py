from .base import Base
from typing import List

from sqlalchemy import (
    Column, DateTime,
    ForeignKeyConstraint,
    Index, Integer,
    Numeric, PrimaryKeyConstraint,
    String, Table,
    UniqueConstraint, Uuid,
    text
)

from sqlalchemy.orm import (
    Mapped, mapped_column, relationship
)

# Base = declarative_base()
# metadata = Base.metadata


class AppointmentStatus(Base):
    __tablename__ = 'appointment_status'
    __table_args__ = (
        PrimaryKeyConstraint('status_id', name='appointment_status_pkey'),
        UniqueConstraint(
            'name_status', name='appointment_status_name_status_key')
    )

    status_id = mapped_column(Uuid)
    name_status = mapped_column(String(50), nullable=False)

    appointments: Mapped[List['Appointments']] = relationship(
        'Appointments', uselist=True, back_populates='fk_status')


class Specialties(Base):
    __tablename__ = 'specialties'
    __table_args__ = (
        PrimaryKeyConstraint('speciality_id', name='specialties_pkey'),
        UniqueConstraint('nome', name='specialties_nome_key')
    )

    speciality_id = mapped_column(Uuid)
    nome = mapped_column(String(50))

    fk_reader: Mapped['Readers'] = relationship(
        'Readers', secondary='reader_specialties', back_populates='fk_speciality')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key'),
        Index('idx_users_email_active', 'email', unique=True)
    )

    user_id = mapped_column(Uuid)
    nome = mapped_column(String(50), nullable=False)
    email = mapped_column(String(100), nullable=False)
    senha_hash = mapped_column(String(255), nullable=False)
    deleted_at = mapped_column(DateTime(True))


class Clients(Users):
    __tablename__ = 'clients'
    __table_args__ = (
        ForeignKeyConstraint(['fk_user_id'], ['users.user_id'],
                             ondelete='RESTRICT', name='fk_clients_user'),
        PrimaryKeyConstraint('fk_user_id', name='clients_pkey')
    )

    fk_user_id = mapped_column(Uuid)

    appointments: Mapped[List['Appointments']] = relationship(
        'Appointments', uselist=True, back_populates='fk_client')


class Readers(Users):
    __tablename__ = 'readers'
    __table_args__ = (
        ForeignKeyConstraint(['fk_user_id'], ['users.user_id'],
                             ondelete='RESTRICT', name='fk_readers_user'),
        PrimaryKeyConstraint('fk_user_id', name='readers_pkey')
    )

    fk_user_id = mapped_column(Uuid)
    foto_url = mapped_column(String(255))
    bio = mapped_column(String(255))

    fk_speciality: Mapped['Specialties'] = relationship(
        'Specialties', secondary='reader_specialties', back_populates='fk_reader')
    appointments: Mapped[List['Appointments']] = relationship(
        'Appointments', uselist=True, back_populates='fk_reader')
    services: Mapped[List['Services']] = relationship(
        'Services', uselist=True, back_populates='fk_reader')


class Appointments(Base):
    __tablename__ = 'appointments'
    __table_args__ = (
        ForeignKeyConstraint(['fk_client_id'], [
                             'clients.fk_user_id'], ondelete='RESTRICT', name='fk_appointment_client'),
        ForeignKeyConstraint(['fk_reader_id'], [
                             'readers.fk_user_id'], ondelete='RESTRICT', name='fk_appointment_reader'),
        ForeignKeyConstraint(['fk_status_id'], [
                             'appointment_status.status_id'], name='fk_appointment_status'),
        PrimaryKeyConstraint('appointment_id', name='appointments_pkey'),
        Index('idx_appointments_client', 'fk_client_id'),
        Index('idx_appointments_reader', 'fk_reader_id')
    )

    appointment_id = mapped_column(Uuid)
    start_datetime = mapped_column(DateTime(True), nullable=False)
    fk_status_id = mapped_column(Uuid, nullable=False)
    fk_reader_id = mapped_column(Uuid, nullable=False)
    fk_client_id = mapped_column(Uuid, nullable=False)
    created_at = mapped_column(
        DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    end_datetime = mapped_column(DateTime(True))
    deleted_at = mapped_column(DateTime(True))

    fk_client: Mapped['Clients'] = relationship(
        'Clients', back_populates='appointments')
    fk_reader: Mapped['Readers'] = relationship(
        'Readers', back_populates='appointments')
    fk_status: Mapped['AppointmentStatus'] = relationship(
        'AppointmentStatus', back_populates='appointments')
    fk_service: Mapped['Services'] = relationship(
        'Services', secondary='appointment_services', back_populates='fk_appointment')


t_reader_specialties = Table(
    'reader_specialties', Base.metadata,
    Column('fk_reader_id', Uuid, nullable=False),
    Column('fk_speciality_id', Uuid, nullable=False),
    ForeignKeyConstraint(['fk_reader_id'], ['readers.fk_user_id'],
                         ondelete='RESTRICT', name='fk_reader_specialties_1'),
    ForeignKeyConstraint(['fk_speciality_id'], [
                         'specialties.speciality_id'], ondelete='RESTRICT', name='fk_reader_specialties_2'),
    PrimaryKeyConstraint('fk_speciality_id', 'fk_reader_id',
                         name='reader_specialties_pkey')
)


class Services(Base):
    __tablename__ = 'services'
    __table_args__ = (
        ForeignKeyConstraint(['fk_reader_id'], [
                             'readers.fk_user_id'], ondelete='RESTRICT', name='fk_service_reader'),
        PrimaryKeyConstraint('service_id', name='services_pkey'),
        Index('idx_services_reader', 'fk_reader_id')
    )

    service_id = mapped_column(Uuid)
    fk_reader_id = mapped_column(Uuid, nullable=False)
    titulo = mapped_column(String(100), nullable=False)
    descricao = mapped_column(String(255), nullable=False)
    duracao_minutes = mapped_column(Integer, nullable=False)
    valor = mapped_column(Numeric(5, 2), nullable=False)
    deleted_at = mapped_column(DateTime(True))

    fk_appointment: Mapped['Appointments'] = relationship(
        'Appointments', secondary='appointment_services', back_populates='fk_service')
    fk_reader: Mapped['Readers'] = relationship(
        'Readers', back_populates='services')


t_appointment_services = Table(
    'appointment_services', Base.metadata,
    Column('fk_service_id', Uuid, nullable=False),
    Column('fk_appointment_id', Uuid, nullable=False),
    ForeignKeyConstraint(['fk_appointment_id'], ['appointments.appointment_id'],
                         ondelete='RESTRICT', name='fk_appointment_services_2'),
    ForeignKeyConstraint(['fk_service_id'], ['services.service_id'],
                         ondelete='RESTRICT', name='fk_appointment_service'),
    PrimaryKeyConstraint('fk_service_id', 'fk_appointment_id',
                         name='appointment_services_pkey'),
    Index('idx_appointment_services_appointment', 'fk_appointment_id'),
    Index('idx_appointment_services_service', 'fk_service_id')
)
