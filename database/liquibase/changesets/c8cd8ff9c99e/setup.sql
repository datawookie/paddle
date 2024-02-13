-- Running upgrade 56711208cd56 -> c8cd8ff9c99e

insert into membership_body (id, acronym, name) values (1, 'BC', 'British Canoeing');
insert into membership_body (id, acronym, name) values (2, 'SCA', 'Scottish Canoe Association');
insert into membership_body (id, acronym, name) values (3, 'CW', 'Canoe Wales');
insert into membership_body (id, acronym, name) values (4, 'CANI', 'Canoe Association of Northern Ireland');

UPDATE alembic_version SET version_num='c8cd8ff9c99e' WHERE alembic_version.version_num = '56711208cd56';
