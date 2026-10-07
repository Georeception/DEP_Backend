import csv
from collections import OrderedDict
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from party.models.locations import County, Constituency, Ward


class Command(BaseCommand):
    help = 'Import counties, constituencies, and wards from the backend data CSV files.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-dir',
            default=settings.BASE_DIR / 'data',
            type=Path,
            help='Directory containing counties.csv, constituencies.csv, and wards.csv.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Validate all CSV data and show the import counts without saving.',
        )

    def handle(self, *args, **options):
        data_dir = options['data_dir']
        counties = self._read_csv(
            data_dir / 'counties.csv',
            ('COUNTRY', 'NAME_1', 'TYPE_1'),
            'TYPE_1',
            'County',
            ('NAME_1',),
            allow_empty_name=True,
        )
        constituencies = self._read_csv(
            data_dir / 'constituencies.csv',
            ('COUNTRY', 'NAME_1', 'NAME_2', 'TYPE_2'),
            'TYPE_2',
            'Constituency',
            ('NAME_1', 'NAME_2'),
        )
        wards = self._read_csv(
            data_dir / 'wards.csv',
            ('COUNTRY', 'NAME_1', 'NAME_2', 'NAME_3', 'TYPE_3'),
            'TYPE_3',
            'Ward',
            ('NAME_1', 'NAME_2', 'NAME_3'),
        )

        county_records = OrderedDict()
        for country, county_name in counties:
            county_records[(country, county_name)] = None

        constituency_records = OrderedDict()
        for country, county_name, constituency_name in constituencies:
            if (country, county_name) not in county_records:
                raise CommandError(
                    f'Constituency {constituency_name!r} references missing county '
                    f'{county_name!r} in {country}.'
                )
            constituency_records[(country, county_name, constituency_name)] = None

        ward_records = OrderedDict()
        for country, county_name, constituency_name, ward_name in wards:
            constituency_key = (country, county_name, constituency_name)
            if constituency_key not in constituency_records:
                raise CommandError(
                    f'Ward {ward_name!r} references missing constituency '
                    f'{constituency_name!r} in {county_name}, {country}.'
                )
            ward_records[(country, county_name, constituency_name, ward_name)] = None

        if options['dry_run']:
            self.stdout.write(
                f'Validated {len(county_records)} counties, '
                f'{len(constituency_records)} constituencies, and '
                f'{len(ward_records)} wards. No records were changed.'
            )
            return

        created = {'counties': 0, 'constituencies': 0, 'wards': 0}
        with transaction.atomic():
            county_objects = {}
            for country, name in county_records:
                county, was_created = County.objects.update_or_create(
                    name=name,
                    defaults={'country': country},
                )
                county_objects[(country, name)] = county
                created['counties'] += was_created

            constituency_objects = {}
            for country, county_name, name in constituency_records:
                constituency, was_created = Constituency.objects.get_or_create(
                    name=name,
                    county=county_objects[(country, county_name)],
                )
                constituency_objects[(country, county_name, name)] = constituency
                created['constituencies'] += was_created

            for country, county_name, constituency_name, name in ward_records:
                _, was_created = Ward.objects.get_or_create(
                    name=name,
                    constituency=constituency_objects[
                        (country, county_name, constituency_name)
                    ],
                )
                created['wards'] += was_created

        self.stdout.write(
            self.style.SUCCESS(
                f'Imported {len(county_records)} counties, '
                f'{len(constituency_records)} constituencies, and '
                f'{len(ward_records)} wards. '
                f'Created {created["counties"]} counties, '
                f'{created["constituencies"]} constituencies, and '
                f'{created["wards"]} wards.'
            )
        )

    def _read_csv(
        self,
        path,
        required_columns,
        type_column,
        expected_type,
        name_columns,
        allow_empty_name=False,
    ):
        if not path.is_file():
            raise CommandError(f'Required location data file not found: {path}')

        records = []
        with path.open(encoding='utf-8-sig', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            missing_columns = set(required_columns) - set(reader.fieldnames or ())
            if missing_columns:
                raise CommandError(
                    f'{path.name} is missing required columns: '
                    f'{", ".join(sorted(missing_columns))}.'
                )

            for line_number, row in enumerate(reader, start=2):
                names = tuple((row.get(column) or '').strip() for column in name_columns)
                if allow_empty_name and not names[0]:
                    continue
                if any(not name for name in names):
                    raise CommandError(
                        f'{path.name}:{line_number} contains an empty location name.'
                    )

                country = (row.get('COUNTRY') or '').strip()
                if not country:
                    raise CommandError(
                        f'{path.name}:{line_number} contains an empty country.'
                    )
                if (row.get(type_column) or '').strip() != expected_type:
                    raise CommandError(
                        f'{path.name}:{line_number} has an unexpected '
                        f'{type_column} value.'
                    )
                records.append((country, *names))

        if not records:
            raise CommandError(f'{path.name} contains no usable location rows.')
        return records
