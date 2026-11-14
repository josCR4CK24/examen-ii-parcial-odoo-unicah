assert env.cr.dbname == 'examen_unicah'
env.ref('unicah_evidencia.estudiante').write({'carrera': 'Ingeniería en Sistemas'})
env.ref('unicah_evidencia.equipo').write({'name': 'Portátil Lenovo - Laboratorio UNICAH'})
env.ref('unicah_evidencia.prestamo').write({'name': 'Préstamo demostrativo UNICAH','observaciones': 'Evidencia académica: equipo entregado en buen estado.'})
env.cr.commit()
print('Textos demostrativos normalizados a UTF-8.')
