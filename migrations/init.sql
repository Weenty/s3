CREATE TABLE files
(
    "id"            bigserial    not null
      primary key,
    "filepath"                text,
    "status" integer
);

CREATE TABLE statuses
(
    "id"            serial    not null
        primary key,
    "value"          varchar(50)
);

INSERT INTO statuses (id, value) VALUES (1, 'pending');
INSERT INTO statuses (id, value) VALUES (2, 'uploaded');
INSERT INTO statuses (id, value) VALUES (3, 'processing');
INSERT INTO statuses (id, value) VALUES (4, 'done');
INSERT INTO statuses (id, value) VALUES (5, 'error');