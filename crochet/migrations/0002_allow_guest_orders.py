from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crochet', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='id_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='orders',
                to='crochet.user',
                verbose_name='Customer',
            ),
        ),
    ]