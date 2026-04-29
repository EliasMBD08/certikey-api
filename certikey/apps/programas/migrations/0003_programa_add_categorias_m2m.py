from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0001_initial'),
        ('programas', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='programa',
            name='categorias',
            field=models.ManyToManyField(
                blank=True,
                related_name='programas_m2m',
                to='catalogos.categoria',
            ),
        ),
    ]
