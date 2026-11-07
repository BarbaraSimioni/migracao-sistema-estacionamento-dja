from django.db import migrations


INITIAL_SPACES = [
    *[(f"A{number:02d}", "CARRO") for number in range(1, 11)],
    *[(f"B{number:02d}", "MOTO") for number in range(1, 6)],
]


def create_initial_spaces(apps, schema_editor):
    parking_space = apps.get_model("api", "Vaga")
    for number, space_type in INITIAL_SPACES:
        parking_space.objects.get_or_create(
            numero=number,
            defaults={"tipo": space_type, "status": "LIVRE"},
        )


def remove_initial_spaces(apps, schema_editor):
    parking_space = apps.get_model("api", "Vaga")
    for number, space_type in INITIAL_SPACES:
        spaces = parking_space.objects.filter(
            numero=number,
            tipo=space_type,
            status="LIVRE",
        )
        for space in spaces:
            if not space.permanencia_set.exists():
                space.delete()


class Migration(migrations.Migration):
    dependencies = [("api", "0001_initial")]

    operations = [
        migrations.RunPython(create_initial_spaces, remove_initial_spaces),
    ]
