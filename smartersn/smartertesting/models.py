from django.db import models

# Create your models here.
class UpdateSet(models.Model):
    # file will be uploaded to MEDIA_ROOT/
    name = models.CharField(max_length=64)
    upload = models.FileField(upload_to='uploads/')

    def __str__(self):
        return f'UpdateSet: {self.name}'

class Upload(models.Model):
    update_set_name =  models.CharField(max_length=80)
    update_set_id = models.CharField(max_length=32)
    description = models.CharField(max_length=4000, blank=True, null=True)

    def __str__(self):
        return f'{self.update_set_name}'


class SNObjectType(models.Model):
    """this class defines the SN object type, some examples are Business rules, script includes, client scripts, etc."""
    name = models.CharField(max_length=128, unique=True)
    code_name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return f'Type: {self.name}'


class SNObject(models.Model):
    """"""
    name = models.CharField(max_length=40)
    # sysids are unique to every record in every table in every instance in the world
    # https://docs.servicenow.com/bundle/jakarta-platform-administration/page/administer/table-administration/concept/c_UniqueRecordIdentifier.html
    sys_id = models.CharField(max_length=32, unique=True)

    object_type = models.ForeignKey(SNObjectType, on_delete=models.CASCADE, related_name="sn_objects")

    def __str__(self):
        return f'{self.object_type.name}: {self.name}'

class SNTest(models.Model):
    """This table stores SN tests for linking together later"""
    name =  models.CharField(max_length=100)
    sys_id = models.CharField(max_length=32, unique=True)
    description = models.TextField()

    def __str__(self):
        return f'Test: {self.name}'

class SNTestObjectRelation(models.Model):
    test =  models.ForeignKey(
        SNTest,
        on_delete=models.CASCADE,
        related_name="related_objects",)

    sn_object =   models.ForeignKey(
        SNObject,
        on_delete=models.CASCADE,
        related_name="related_tests",)

    description = models.CharField(max_length=400)

    class Meta:
        unique_together = ('test', 'sn_object')

    def __str__(self):
        return f'{self.test} - {self.sn_object}'

class ObjectUploadRelation(models.Model):
    upload =  models.ForeignKey(
        Upload,
        on_delete=models.CASCADE,
        related_name="updates",)

    sn_object =   models.ForeignKey(
        SNObject,
        on_delete=models.CASCADE,
        related_name="uploads",)

    class Meta:
        unique_together = ('upload', 'sn_object')

    def __str__(self):
        return f'{self.upload} - {self.sn_object}'
