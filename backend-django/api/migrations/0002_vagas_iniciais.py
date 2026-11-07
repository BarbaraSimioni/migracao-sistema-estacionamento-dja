from django.db import migrations


def criar_vagas(apps, schema_editor):
    Vaga = apps.get_model('api', 'Vaga')

    for numero in range(1, 11):
        Vaga.objects.get_or_create(
            numero=f'A{numero:02d}',
            defaults={'tipo': 'CARRO'},
        )

    for numero in range(1, 6):
        Vaga.objects.get_or_create(
            numero=f'B{numero:02d}',
            defaults={'tipo': 'MOTO'},
        )


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(criar_vagas, migrations.RunPython.noop),
    ]
