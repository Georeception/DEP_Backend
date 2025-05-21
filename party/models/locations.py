from django.db import models

class County(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Counties"
        ordering = ['name']

    def __str__(self):
        return self.name

class Constituency(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='constituencies')

    class Meta:
        verbose_name_plural = "Constituencies"
        ordering = ['name']
        unique_together = ['name', 'county']

    def __str__(self):
        return f"{self.name} - {self.county.name}"

class Ward(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='wards')

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'constituency']

    def __str__(self):
        return f"{self.name} - {self.constituency.name}" 