drop table if exists entries;
create table entries (
	id integer primary key autoincrement,
	email text not null,
	pledge numeric (10, 2) not null
);