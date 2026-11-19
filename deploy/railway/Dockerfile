FROM odoo:20.0@sha256:8bcae4c1f895683ee851e19dd3e7d999e81e770defe9015bc9dad8bbf10f2b0d
USER root
ENV HOME=/var/lib/odoo
COPY --chown=odoo:odoo addons/ /mnt/extra-addons/
COPY scripts/bootstrap.py /opt/unicah/bootstrap.py
COPY scripts/sync_admin.py /opt/unicah/sync_admin.py
COPY scripts/verify_runtime.py /opt/unicah/verify_runtime.py
ENTRYPOINT ["python3", "/opt/unicah/bootstrap.py"]
CMD []
