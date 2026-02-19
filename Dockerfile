# Odoo 19.0
FROM odoo:19.0

USER root

# Copy custom addons
COPY custom_addons /mnt/extra-addons

# Set permissions
RUN chown -R odoo:odoo /mnt/extra-addons

USER odoo

