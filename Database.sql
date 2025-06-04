-- Slet og genopret brugeren 'testuser'
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'testuser') THEN
        REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM testuser;
        REVOKE ALL PRIVILEGES ON SCHEMA public FROM testuser;
        REVOKE ALL PRIVILEGES ON DATABASE "TINProject" FROM testuser;
        DROP ROLE testuser;
    END IF;
END $$;

-- Opret brugeren
CREATE ROLE testuser WITH LOGIN PASSWORD '123';

-- Giv adgang til databasen
GRANT ALL PRIVILEGES ON DATABASE "TINProject" TO testuser;

-- Skift til databasen (hvis du kører dette manuelt)
\c "TINProject"

-- DROP tables hvis de eksisterer
DROP TABLE IF EXISTS public."People";
DROP TABLE IF EXISTS public."Employers";
DROP TABLE IF EXISTS public."Countries";
DROP TABLE IF EXISTS public."Highscores";

-- Opret Countries-tabel
CREATE TABLE public."Countries" (
    code VARCHAR PRIMARY KEY,
    name VARCHAR,
    format VARCHAR,
    example VARCHAR
);

-- Opret Employers-tabel med autogenereret ID
CREATE TABLE public."Employers" (
    "EmployerID" SERIAL PRIMARY KEY,
    "Name" VARCHAR,
    "Country_ID" VARCHAR REFERENCES public."Countries"(code)
);

-- Opret People-tabel
CREATE TABLE public."People" (
    "CPR_nr" VARCHAR PRIMARY KEY,
    "F_name" VARCHAR,
    "Surname" VARCHAR,
    "EmployerID" INTEGER REFERENCES public."Employers"("EmployerID"),
    "Country_ID" VARCHAR REFERENCES public."Countries"(code),
    "TIN_value" VARCHAR,
    "TIN_type" VARCHAR,
    "Start_Date" DATE,
    "End_Date" DATE,
    "TIN_status" VARCHAR
);

-- Opret Highscores-tabel
CREATE TABLE public."Highscores" (
    "Timestamp" TIMESTAMP,
    "Name" VARCHAR(100),
    "Score" INTEGER
);

-- Giv privilegier
GRANT SELECT, INSERT, UPDATE, DELETE ON public."People" TO testuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON public."Employers" TO testuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON public."Countries" TO testuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON public."Highscores" TO testuser;

-- Giv adgang til sekvenser (nødvendigt for SERIAL/autoincrement)
GRANT USAGE, SELECT, UPDATE ON SEQUENCE public."Employers_EmployerID_seq" TO testuser;

-- Indlæs data fra CSV
COPY public."Countries" FROM '/Users/kevinkinsella/Desktop/Project/Data/Countries.csv' DELIMITER ',' CSV HEADER;
COPY public."Employers" FROM '/Users/kevinkinsella/Desktop/Project/Data/Employers.csv' DELIMITER ',' CSV HEADER;
COPY public."People" FROM '/Users/kevinkinsella/Desktop/Project/Data/People.csv' DELIMITER ',' CSV HEADER;
