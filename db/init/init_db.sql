CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

--create enums

--create base tables

drop table if exists species;
create table if not exists species (
    id uuid default uuid_generate_v4() primary key not null,
    name varchar not null,
    base_attack int default 1 not null,
    base_hp int default 1 not null,
    base_speed int default 1 not null,
);

drop table if exists creature;
create table if not exists creature (
    id uuid default uuid_generate_v4() primary key  not null,
    species_id uuid foreign key references species not null,
    player_id uuid foreign key references player,
    level int default 1 not null,
    current_hp int default 1 not null,
    nickname varchar
);

drop table if exists player;
create table if not exists player (
    id uuid default uuid_generate_v4() primary key  not null,
    name varchar unique not null
);

drop table if exists match;
create table if not exists match (
    id uuid default uuid_generate_v4() primary key  not null,
    turn int default 1 not null,
    is_finished boolean default false not null,
);

-- create join tables

drop table if exists match_players;
create table matches_players (
    match_id uuid foreign key references match not null,
    player_id uuid foreign key references player not null,
    constraint unique (match_id, player_id)
);


-- test data

insert into player (name) values
('Safari'),
('Firehawk');

insert into species (name) values
('Test Species');

insert into creature (species_id, player_id, nickname)values
(
    select id from species where name = 'Test Species',
    select id from players where name = 'Safari',
    'Gatr'
),
(
    select id from species where name = 'Test Species',
    select id from players where name = 'Firehawk',
    'Mouse'
);