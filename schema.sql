DROP TABLE IF EXISTS encrypt;

create table encrypt(
    id Integer PRIMARY KEY AUTOINCREMENT,
    encrypt_key text Not Null,
    is_used boolean default = 0
)