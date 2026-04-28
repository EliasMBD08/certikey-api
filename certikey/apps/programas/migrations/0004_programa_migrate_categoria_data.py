from django.db import migrations


def copiar_categoria_a_categorias(apps, schema_editor):
    Programa = apps.get_model('programas', 'Programa')
    for programa in Programa.objects.filter(categoria__isnull=False):
        programa.categorias.add(programa.categoria_id)


def revertir_categorias_a_categoria(apps, schema_editor):
    Programa = apps.get_model('programas', 'Programa')
    for programa in Programa.objects.all():
        primera = programa.categorias.first()
        if primera:
            programa.categoria_id = primera.id
            programa.save(update_fields=['categoria_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('programas', '0003_programa_add_categorias_m2m'),
    ]

    operations = [
        migrations.RunPython(
            copiar_categoria_a_categorias,
            reverse_code=revertir_categorias_a_categoria,
        ),
    ]
