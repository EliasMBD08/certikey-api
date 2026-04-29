import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0001_initial'),
        ('programas', '0004_programa_migrate_categoria_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programa',
            name='categorias',
            field=models.ManyToManyField(
                blank=True,
                related_name='programas',
                to='catalogos.categoria',
            ),
        ),
        migrations.RemoveField(
            model_name='programa',
            name='categoria',
        ),
    ]
