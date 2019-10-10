UPDATE ir_cron SET active='f';
UPDATE ir_mail_server SET active='f', smtp_encryption='none', smtp_port=1025, smtp_host='localhost',smtp_user='', smtp_pass='';
UPDATE fetchmail_server SET active='f', password='', server='localhost';
update  res_users set password='admin'  where login='admin';
