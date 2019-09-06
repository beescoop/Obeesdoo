FROM odoo:9.0

USER root
RUN printf "deb http://archive.debian.org/debian/ jessie main\ndeb-src http://archive.debian.org/debian/ jessie main\ndeb http://security.debian.org jessie/updates main\ndeb-src http://security.debian.org jessie/updates main" > /etc/apt/sources.list
RUN apt-get update && apt-get install -y git wget gcc python-dev libssl-dev libffi-dev make

##### 10) Installer wkhtml to pdf 0.12.1 !! (pas une autre) (sur une machine 64 bit avec un ubuntu 64bit 14.04)
# RUN apt-get install -y fontconfig  libfontconfig1 libxrender1 fontconfig-config libjpeg-turbo8-dev && \
#     wget --quiet https://downloads.wkhtmltopdf.org/0.12/0.12.5/wkhtmltox_0.12.5-1.trusty_amd64.deb && \
#     dpkg -i wkhtmltox_0.12.5-1.trusty_amd64.deb && \
#     ln -s /usr/local/bin/wkhtmltoimage /usr/bin/wkhtmltoimage && \
#     ln -s /usr/local/bin/wkhtmltopdf /usr/bin/wkhtmltopdf

RUN mkdir -p /app/extra-addons &&  chown odoo /app/extra-addons

USER odoo
RUN git clone https://github.com/beescoop/Obeesdoo.git /app/extra-addons/obeesdoo -b 9.0 --depth 1 && \
	git clone https://github.com/coopiteasy/vertical-cooperative.git /app/extra-addons/vertical-cooperative -b 9.0 --depth 1 && \
	git clone https://github.com/coopiteasy/addons.git /app/extra-addons/houssine-addons -b 9.0 --depth 1 && \
	git clone https://github.com/coopiteasy/procurement-addons /app/extra-addons/procurement-addons -b 9.0 --depth 1 && \
	git clone https://www.github.com/OCA/l10n-belgium /app/extra-addons/l10n-belgium -b 9.0 --depth 1 && \
	git clone https://www.github.com/OCA/mis-builder /app/extra-addons/mis-builder -b 9.0 --depth 1 && \
	git clone https://www.github.com/OCA/web /app/extra-addons/web -b 9.0 --depth 1   && \
	git clone https://github.com/OCA/server-tools /app/extra-addons/server-tools -b 9.0 --depth 1 && \
	git clone https://github.com/OCA/reporting-engine /app/extra-addons/reporting-engine -b 9.0 --depth 1

USER root
RUN pip install --upgrade  setuptools enum
RUN pip install -r /app/extra-addons/reporting-engine/requirements.txt
RUN pip install -r /app/extra-addons/server-tools/requirements.txt
RUN pip install -r /app/extra-addons/obeesdoo/requirements.txt

USER odoo

# COPY example_odoo.conf /etc/odoo/openerp-server.conf
