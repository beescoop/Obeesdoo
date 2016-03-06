# Obeesdoo



# Migrate barcode
```sql
insert into member_card (active, barcode, partner_id, responsible_id, activation_date) select 't', barcode, id, 1, '2016-01-01' from res_partner where barcode is not null;
update res_partner set eater = 'worker_eater' where barcode is not null;
```