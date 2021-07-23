FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

# Install the basics
RUN ln -fs /usr/share/zoneinfo/Europe/Brussels /etc/localtime && \
    apt-get update && apt-get install -y curl git postgresql python3-psycopg2 python3-pip && \
    dpkg-reconfigure --frontend noninteractive tzdata

# Install wkhtmltopdf 0.12.5
RUN curl -L https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb \
    --output wkhtmltox_0.12.5-1.bionic_amd64.deb && \
    (dpkg -i wkhtmltox_0.12.5-1.bionic_amd64.deb || apt-get -f install -y) && \
    ln -s /usr/local/bin/wkhtmltoimage /usr/bin/wkhtmltoimage && \
    ln -s /usr/local/bin/wkhtmltopdf /usr/bin/wkhtmltopdf && \
    rm -f wkhtmltox_0.12.5-1.bionic_amd64.deb

# Node (ubuntu 14 version of node is Old as f*)
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g less less-plugin-clean-css


RUN useradd -ms /bin/bash odoo
USER odoo
RUN mkdir -p /home/odoo/extra-addons
WORKDIR /home/odoo
RUN git clone https://github.com/coopiteasy/OCB.git /home/odoo/odoo -b 12.0 --depth 1 && \
	git clone https://github.com/coopiteasy/addons.git /home/odoo/addons -b 12.0 --depth 1 && \
    git clone https://github.com/beescoop/Obeesdoo.git /home/odoo/obeesdoo -b 12.0 --depth 1 && \
    git clone https://github.com/OCA/partner-contact.git /home/odoo/partner-contact -b 12.0 --depth 1 && \
	# git clone https://github.com/coopiteasy/procurement-addons.git /home/odoo/procurement-addons -b 12.0 --depth 1 && \
	git clone https://github.com/coopiteasy/vertical-cooperative.git /home/odoo/vertical-cooperative -b 12.0 --depth 1 && \
	git clone https://github.com/coopiteasy/account-financial-reporting.git /home/odoo/account-financial-reporting -b 12.0 --depth 1 && \
	git clone https://github.com/coopiteasy/account-financial-tools.git /home/odoo/account-financial-tools -b 12.0 --depth 1 && \
	git clone https://github.com/coopiteasy/bank-payment.git /home/odoo/bank-payment -b 12.0 --depth 1 && \
	git clone https://github.com/coopiteasy/l10n-belgium.git /home/odoo/l10n-belgium -b 12.0 --depth 1 && \
	git clone https://github.com/coopiteasy/mis-builder.git /home/odoo/mis-builder -b 12.0 --depth 1 && \
	git clone https://github.com/coopiteasy/pos.git /home/odoo/pos -b 12.0 --depth 1   && \
	git clone https://github.com/coopiteasy/reporting-engine.git /home/odoo/reporting-engine -b 12.0 --depth 1 && \
	git clone https://github.com/coopiteasy/server-tools.git /home/odoo/server-tools -b 12.0 --depth 1 && \
	git clone https://github.com/coopiteasy/web.git /home/odoo/web -b 12.0 --depth 1   && \
	git clone https://github.com/coopiteasy/website.git /home/odoo/website -b 12.0 --depth 1 && \
	echo "That's all folks!"

USER root
# RUN pip4 install --upgrade pip
# adding dependencies here so that we don't have to rebuild the previous steps if it changes.
# python3 c header files
# pillow dependencies
# more pillow dependencies
# python3-lxml
# python3-ldap
RUN apt-get install -y python3-dev \
                       libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev \
                       libwebp-dev tcl8.6-dev tk8.6-dev \
                       libxml2-dev libxslt1-dev \
                       libsasl2-dev libldap2-dev libssl-dev


USER odoo
# Installing in user space because system-libraries cannot be uninstalled and conflict.
# Simpler than creating a virtualenv
RUN sed -i '/psycopg2/d' /home/odoo/odoo/requirements.txt && \
    sed -i '/python3-ldap/d' /home/odoo/odoo/requirements.txt && \
    sed -i '/xlwt/d' /home/odoo/odoo/requirements.txt && \
    sed -i '/xlrd/d' /home/odoo/odoo/requirements.txt && \
    pip3 install --user -r /home/odoo/odoo/requirements.txt \
                        -r /home/odoo/reporting-engine/requirements.txt \
                        -r /home/odoo/server-tools/requirements.txt

WORKDIR /home/odoo/odoo
CMD python3 odoo.py
