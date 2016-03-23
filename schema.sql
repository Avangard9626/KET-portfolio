drop table if exists students;
drop table if exists portfolio;
drop table if exists users;
create table students(
  id integer key not null,
  first_name text not null,
  second_name text not null,
  third_name text not null,
  sex boolean not null,
  birthday DATE not null,
  about_me text not null,
  group_name text not null
);

create table portfolio(
  id integer primary key autoincrement,
  text text not null,
  image text not null,
  student_id integer key not null
);

create table users(
  id integer primary key autoincrement,
  login text not null,
  password text not null,
  email text not null
);