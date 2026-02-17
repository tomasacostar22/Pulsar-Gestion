from django.db import migrations


def crear_horarios(apps, schema_editor):
    Usuario = apps.get_model("usuarios", "Usuario")
    HorarioLaboral = apps.get_model("administrativo", "HorarioLaboral")

    for usuario in Usuario.objects.all():
        HorarioLaboral.objects.get_or_create(
            empleado=usuario,
            defaults={
                "lunes_entrada": "07:00",
                "lunes_salida": "16:00",
                "martes_entrada": "07:00",
                "martes_salida": "16:00",
                "miercoles_entrada": "07:00",
                "miercoles_salida": "16:00",
                "jueves_entrada": "07:00",
                "jueves_salida": "16:00",
                "viernes_entrada": "07:00",
                "viernes_salida": "16:00",
                "sabado_entrada": "07:00",
                "sabado_salida": "12:00",
            },
        )


def borrar_horarios(apps, schema_editor):
    HorarioLaboral = apps.get_model("administrativo", "HorarioLaboral")
    HorarioLaboral.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("administrativo", "0001_initial"),
        ("usuarios", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(crear_horarios, borrar_horarios),
    ]
