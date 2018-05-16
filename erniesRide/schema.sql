drop table if exists entries;
create table entries (
	id integer primary key autoincrement,
	email text not null,
	firstName text not null,
	lastName text not null,
	city text not null,
	state text not null,
	pledge numeric (10, 2) not null,
	riderName text not null
);