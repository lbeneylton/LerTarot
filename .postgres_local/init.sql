/* Modelo Físico */

CREATE TABLE Users (
    user_id UUID PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    deleted_at TIMESTAMPTZ NULL
);

CREATE UNIQUE INDEX idx_users_email_active
ON Users(email) 
WHERE deleted_at IS NULL;

CREATE TABLE Clients (
    fk_user_id UUID PRIMARY KEY
);

CREATE TABLE Readers (
    fk_user_id UUID PRIMARY KEY,
    foto_url VARCHAR(255),
    bio VARCHAR(255)
);

CREATE TABLE Appointments (
    appointment_id UUID PRIMARY KEY,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    start_datetime TIMESTAMPTZ NOT NULL,
    end_datetime TIMESTAMPTZ NULL,

    fk_status_id UUID NOT NULL,
    fk_reader_id UUID NOT NULL,
    fk_client_id UUID NOT NULL,
    deleted_at TIMESTAMPTZ NULL --Adicionado soft delete para agendamentos
);

CREATE TABLE Services (
    service_id UUID PRIMARY KEY,
    fk_reader_id UUID NOT NULL,

    titulo VARCHAR(100) NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    duracao_minutes INTEGER NOT NULL,
    valor DECIMAL(5,2) NOT NULL,
    deleted_at TIMESTAMPTZ NULL
);

CREATE TABLE Specialties(
    speciality_id UUID PRIMARY KEY,
    nome VARCHAR(50) UNIQUE
);

CREATE TABLE appointment_status (
    status_id UUID PRIMARY KEY,
    name_status VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE appointment_services (
    fk_service_id UUID,
    fk_appointment_id UUID,
    PRIMARY KEY (fk_service_id, fk_appointment_id)
);

CREATE TABLE reader_specialties (
    fk_reader_id UUID,
    fk_speciality_id UUID,
    PRIMARY KEY (fk_speciality_id, fk_reader_id)
);
 

/* ALTERAÇÕES NAS CONSTRAINTS (ON DELETE ALTERADOS)*/ 

-- Regras para a tabela Users

ALTER TABLE Clients 
ADD CONSTRAINT FK_Clients_User
FOREIGN KEY (fk_user_id)
REFERENCES Users (user_id)
ON DELETE RESTRICT;
 
ALTER TABLE Readers 
ADD CONSTRAINT FK_Readers_User
FOREIGN KEY (fk_user_id)
REFERENCES Users (user_id)
ON DELETE RESTRICT;
 
-- Regras para a tabela Appointments

ALTER TABLE Appointments 
ADD CONSTRAINT FK_Appointment_status
FOREIGN KEY (fk_status_id)
REFERENCES appointment_status (status_id)
ON DELETE NO ACTION;
 
ALTER TABLE Appointments 
ADD CONSTRAINT FK_Appointment_Reader
FOREIGN KEY (fk_reader_id)
REFERENCES Readers (fk_user_id)
ON DELETE RESTRICT; -- Mantém histórico de agendamentos
 
ALTER TABLE Appointments 
ADD CONSTRAINT FK_Appointment_Client
FOREIGN KEY (fk_client_id)
REFERENCES Clients (fk_user_id)
ON DELETE RESTRICT;
 
ALTER TABLE Services
ADD CONSTRAINT FK_Service_Reader
FOREIGN KEY (fk_reader_id)
REFERENCES Readers (fk_user_id)
ON DELETE RESTRICT;
 
ALTER TABLE appointment_services 
ADD CONSTRAINT FK_appointment_service
FOREIGN KEY (fk_service_id)
REFERENCES Services (service_id)
ON DELETE RESTRICT;
 
ALTER TABLE appointment_services 
ADD CONSTRAINT FK_appointment_services_2
FOREIGN KEY (fk_appointment_id)
REFERENCES Appointments (appointment_id)
ON DELETE RESTRICT; -- Se o agendamento for apagado, mantém o historico
 
ALTER TABLE reader_specialties 
ADD CONSTRAINT FK_reader_specialties_1
FOREIGN KEY (fk_reader_id)
REFERENCES Readers (fk_user_id)
ON DELETE RESTRICT;
 
ALTER TABLE reader_specialties 
ADD CONSTRAINT FK_reader_specialties_2
FOREIGN KEY (fk_speciality_id)
REFERENCES Specialties(speciality_id)
ON DELETE RESTRICT;

-- 

CREATE INDEX idx_appointments_reader
ON Appointments(fk_reader_id);

CREATE INDEX idx_appointments_client
ON Appointments(fk_client_id);

CREATE INDEX idx_services_reader
ON Services(fk_reader_id);

CREATE INDEX idx_appointment_services_appointment
ON appointment_services(fk_appointment_id);

CREATE INDEX idx_appointment_services_service
ON appointment_services(fk_service_id);


--
CREATE FUNCTION validate_service_reader()
RETURNS TRIGGER AS $$
BEGIN

    IF (
        SELECT a.fk_reader_id
        FROM Appointments a
        WHERE a.appointment_id = NEW.fk_appointment_id
    ) != (
        SELECT s.fk_reader_id
        FROM Services s
        WHERE s.service_id = NEW.fk_service_id
    )
    THEN
        RAISE EXCEPTION 'Service belongs to another reader';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_validate_service_reader
BEFORE INSERT ON appointment_services
FOR EACH ROW
EXECUTE FUNCTION validate_service_reader();