import pandas as pd
from django.core.management.base import BaseCommand
from party.models.locations import County, Constituency, Ward
from django.db import transaction

class Command(BaseCommand):
    help = 'Import locations data from Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Path to the Excel file')

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']
        
        try:
            # Read Excel file
            df = pd.read_excel(excel_file)
            
            # Clean the data
            df['County'] = df['County'].str.strip()
            df['Constituency'] = df['Constituency'].str.strip()
            df['Ward'] = df['Ward'].str.strip()

            # Get unique counties with their codes
            unique_counties = df[['County']].drop_duplicates()
            
            with transaction.atomic():
                # Process counties
                for _, county_row in unique_counties.iterrows():
                    county_name = county_row['County']
                    county, created = County.objects.get_or_create(
                        name=county_name
                    )
                    if created:
                        self.stdout.write(f"Created county: {county_name}")

                # Get unique constituencies per county
                for county in County.objects.all():
                    county_constituencies = df[
                        (df['County'] == county.name)
                    ][['Constituency']].drop_duplicates()

                    # Process constituencies for this county
                    for _, const_row in county_constituencies.iterrows():
                        constituency_name = const_row['Constituency']
                        constituency, created = Constituency.objects.get_or_create(
                            name=constituency_name,
                            county=county
                        )
                        if created:
                            self.stdout.write(f"Created constituency: {constituency_name} in {county.name}")

                        # Get wards for this constituency
                        constituency_wards = df[
                            (df['County'] == county.name) & 
                            (df['Constituency'] == constituency_name)
                        ][['Ward']].drop_duplicates()

                        # Process wards for this constituency
                        for _, ward_row in constituency_wards.iterrows():
                            ward_name = ward_row['Ward']
                            ward, created = Ward.objects.get_or_create(
                                name=ward_name,
                                constituency=constituency
                            )
                            if created:
                                self.stdout.write(f"Created ward: {ward_name} in {constituency_name}")

            self.stdout.write(self.style.SUCCESS('Successfully imported locations data'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {str(e)}'))
            raise e 