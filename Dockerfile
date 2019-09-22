FROM ubuntu:14.04
# Starting from ubuntu 14 as its the only one really supported for wkhtmltopdf (I don't like hacking around).
# Also its a docker image, not a server.

ENV DEBIAN_FRONTEND=noninteractive

# Install the basics
RUN ln -fs /usr/share/zoneinfo/Europe/Brussels /etc/localtime && \
    apt-get update && apt-get install -y curl git postgresql python-psycopg2 python-pip && \
    dpkg-reconfigure --frontend noninteractive tzdata

# Install wkhtmltopdf 0.12.1
RUN curl -L https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.1/wkhtmltox-0.12.1_linux-trusty-amd64.deb \
    --output wkhtmltox-0.12.1_linux-trusty-amd64.deb && \
    (dpkg -i wkhtmltox-0.12.1_linux-trusty-amd64.deb || apt-get -f install -y) && \
    ln -s /usr/local/bin/wkhtmltoimage /usr/bin/wkhtmltoimage && \
    ln -s /usr/local/bin/wkhtmltopdf /usr/bin/wkhtmltopdf && \
    rm -f wkhtmltox-0.12.1_linux-trusty-amd64.deb

# Node (ubuntu 14 version of node is Old as f*)
RUN curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash - && \
    apt-get install -y nodejs && \
    npm install -g less less-plugin-clean-css


RUN useradd -ms /bin/bash odoo
USER odoo
RUN mkdir -p /home/odoo/extra-addons
WORKDIR /home/odoo
RUN git clone https://github.com/coopiteasy/OCB.git /home/odoo/odoo -b 9.0 --depth 1 && \
	git clone https://github.com/coopiteasy/addons.git /home/odoo/addons -b 9.0 --depth 1 && \
    git clone https://github.com/beescoop/Obeesdoo.git /home/odoo/obeesdoo -b 9.0 --depth 1 && \
	git clone https://github.com/coopiteasy/procurement-addons.git /home/odoo/procurement-addons -b 9.0 --depth 1 && \
	git clone https://github.com/coopiteasy/vertical-cooperative.git /home/odoo/vertical-cooperative -b 9.0 --depth 1 && \
	git clone https://github.com/coopiteasy/account-financial-reporting.git /home/odoo/account-financial-reporting -b 9.0 --depth 1 && \
	git clone https://github.com/coopiteasy/account-financial-tools.git /home/odoo/account-financial-tools -b 9.0 --depth 1 && \
	git clone https://github.com/coopiteasy/bank-payment.git /home/odoo/bank-payment -b 9.0 --depth 1 && \
	git clone https://github.com/coopiteasy/l10n-belgium.git /home/odoo/l10n-belgium -b 9.0 --depth 1 && \
	git clone https://github.com/coopiteasy/mis-builder.git /home/odoo/mis-builder -b 9.0 --depth 1 && \
	git clone https://github.com/coopiteasy/pos.git /home/odoo/pos -b 9.0 --depth 1   && \
	git clone https://github.com/coopiteasy/reporting-engine.git /home/odoo/reporting-engine -b 9.0 --depth 1 && \
	git clone https://github.com/coopiteasy/server-tools.git /home/odoo/server-tools -b 9.0 --depth 1 && \
	git clone https://github.com/coopiteasy/web.git /home/odoo/web -b 9.0 --depth 1   && \
	git clone https://github.com/coopiteasy/website.git /home/odoo/website -b 9.0 --depth 1 && \
	echo "That's all folks!"


USER root
RUN pip install --upgrade pip
# adding dependencies here so that we don't have to rebuild the previous steps if it changes.
# python c header files
# pillow dependencies
# more pillow dependencies
# python-lxml
# python-ldap
RUN apt-get install -y python-dev \
                       libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev \
                       libwebp-dev tcl8.6-dev tk8.6-dev \
                       libxml2-dev libxslt1-dev \
                       libsasl2-dev libldap2-dev libssl-dev


USER odoo
# Installing in user space because system-libraries cannot be uninstalled and conflict.
# Simpler than creating a virtualenv
RUN sed -i '/psycopg2/d' /home/odoo/odoo/requirements.txt && \
    sed -i '/xlwt/d' /home/odoo/odoo/requirements.txt && \
    sed -i '/python-ldap/d' /home/odoo/odoo/requirements.txt && \
    pip install --user -r /home/odoo/odoo/requirements.txt \
                       -r /home/odoo/reporting-engine/requirements.txt \
                       -r /home/odoo/server-tools/requirements.txt \
                       -r /home/odoo/obeesdoo/requirements.txt \
                       -r /home/odoo/pos/requirements.txt

WORKDIR /home/odoo/odoo
CMD python odoo.py
