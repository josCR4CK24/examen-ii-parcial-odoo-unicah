# Ejecutar con odoo-bin shell, solo en examen_unicah.
assert env.cr.dbname == "examen_unicah"
for xmlid, original_id, duplicate_id in [("convenio_estudiantes", 1, 4), ("convenio_docentes", 2, 5)]:
    original = env["tienda.convenio"].browse(original_id).exists()
    duplicate = env["tienda.convenio"].browse(duplicate_id).exists()
    assert original and original.porcentaje in (15, 10)
    data = env["ir.model.data"].search([("module", "=", "tienda_unicah"), ("name", "=", xmlid)])
    data.write({"res_id": original.id})
    if duplicate:
        assert duplicate.fecha_inicio.isoformat() == "2026-01-01"
        duplicate.active = False
print("Convenios originales vinculados; registros auxiliares archivados sin eliminación.")
env.cr.commit()
