DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'testuser') THEN
        REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM testuser;
        REVOKE ALL PRIVILEGES ON SCHEMA public FROM testuser;
        REVOKE ALL PRIVILEGES ON DATABASE "TINProject" FROM testuser;
        DROP ROLE testuser;
    END IF;
END $$;

CREATE ROLE testuser WITH LOGIN PASSWORD '123';

GRANT ALL PRIVILEGES ON DATABASE "TINProject" TO testuser;

DROP TABLE IF EXISTS public."People";
DROP TABLE IF EXISTS public."Employers";
DROP TABLE IF EXISTS public."Countries";
DROP TABLE IF EXISTS public."Highscores";

CREATE TABLE public."Countries" (
    code VARCHAR PRIMARY KEY,
    name VARCHAR,
    format VARCHAR,
    example VARCHAR
);

CREATE TABLE public."Employers" (
    "EmployerID" SERIAL PRIMARY KEY,
    "Name" VARCHAR,
    "Country_ID" VARCHAR REFERENCES public."Countries"(code)
);

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

CREATE TABLE public."Highscores" (
    "Timestamp" TIMESTAMP,
    "Name" VARCHAR(100),
    "Score" INTEGER
);

GRANT SELECT, INSERT, UPDATE, DELETE ON public."People" TO testuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON public."Employers" TO testuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON public."Countries" TO testuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON public."Highscores" TO testuser;

GRANT USAGE, SELECT, UPDATE ON SEQUENCE public."Employers_EmployerID_seq" TO testuser;

COPY public."Countries" FROM '/Users/kevinkinsella/Desktop/DIS_Project/Data/Countries.csv' DELIMITER ',' CSV HEADER;
COPY public."Employers" FROM '/Users/kevinkinsella/Desktop/DIS_Project/Data/Employers.csv' DELIMITER ',' CSV HEADER;
COPY public."People" FROM '/Users/kevinkinsella/Desktop/DIS_Project/Data/People.csv' DELIMITER ',' CSV HEADER;
