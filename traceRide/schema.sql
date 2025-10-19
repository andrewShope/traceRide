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

create table site_info (
	id integer primary key autoincrement,
	title text not null,
	contents text not null
);

create table articles (
	id integer primary key autoincrement,
	title text not null,
	contents text not null
);

create table riders (
	id integer primary key autoincrement,
	riderName text not null
);

create table email_queue (
	id integer primary key autoincrement,
	email_address text not null,
	first_name text not null,
	last_name text not null,
	pledged_rider text not null,
	pledged_amount text not null,
	email_sent integer not null
	);

insert into articles (title, contents) values ('main-article', 'init');

insert into site_info (title, contents) values ('autoEmailMessage', '');

insert into site_info (title, contents) 
	values 
	('websiteTitle', 'Tennessee Trace Ride'),
	('isSponsorActive', 'TRUE'),
	('activeSponsorMessage', ''),
	('inactiveSponsorMessage', '');


