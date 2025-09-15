drop table if exists entries;
create table entries (
	id integer primary key autoincrement,
	email text not null,
	firstName text not null,
	lastName text not null,
	city text not null,
	state text not null,
	pledge numeric (10, 2) not null,
	riderName text not null,
	donationCenter text not null
);

create table riders (
	id integer primary key autoincrement,
	riderName text not null
);

create table centers (
	id integer primary key autoincrement,
	title text not null,
	contents text not null
);

create table past_rides (
	id integer primary key autoincrement,
	title text not null,
	contents text not null
);

create table articles (
	id integer primary key autoincrement,
	title text not null,
	contents text not null
);

create table site_info (
	id integer primary key autoincrement,
	title text not null,
	contents text not null
);