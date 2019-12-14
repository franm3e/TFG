-- CREATING DATABASE 
CREATE DATABASE "TFG"
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1;

-- CREATING MAIN TABLE
CREATE TABLE public.blocks_details
(
    "C1_plots_number" integer,
    "C2_plots_number" integer,
    "L1_plots_number" integer,
    "L2_plots_number" integer,
    x_block_coordinate real,
    y_block_coordinate real,
    "OBJECTID" integer,
    "CODMANZANA" integer,
    "CODSECTOR" integer,
    "CODSUBSECTOR" integer,
    x_centroid_coordinate real,
    y_centroid_coordinate real,
    x_true_centroid_coordinate real,
    y_true_centroid_coordinate real,
    block_area real,
    block_length real,
    "C1_length" real,
    "C2_length" real,
    "L1_length" real,
    "L2_length" real,
    block_apexes_number integer,
    rectangular_form boolean,
    square_form boolean,
    is_multipart boolean
)
WITH (
    OIDS = FALSE
);

ALTER TABLE public.blocks_details
    OWNER to postgres;