import csv
import json
import xml.etree.ElementTree as ET
import os
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from poi.models import PointOfInterest


class Command(BaseCommand):
    help = 'Import Points of Interest from CSV, JSON, or XML files'

    def add_arguments(self, parser):
        parser.add_argument(
            'files',
            nargs='+',
            type=str,
            help='Path to one or more files to import (CSV, JSON, or XML)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing PoI data...')
            PointOfInterest.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        total_imported = 0
        
        for file_path in options['files']:
            if not os.path.exists(file_path):
                raise CommandError(f'File "{file_path}" does not exist.')
            
            self.stdout.write(f'Processing file: {file_path}')
            
            try:
                imported_count = self.import_file(file_path)
                total_imported += imported_count
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully imported {imported_count} records from {file_path}')
                )
            except Exception as e:
                raise CommandError(f'Error processing file "{file_path}": {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Total records imported: {total_imported}')
        )

    def import_file(self, file_path):
        """Import data from a single file based on its extension"""
        _, ext = os.path.splitext(file_path.lower())
        
        if ext == '.csv':
            return self.import_csv(file_path)
        elif ext == '.json':
            return self.import_json(file_path)
        elif ext == '.xml':
            return self.import_xml(file_path)
        else:
            raise CommandError(f'Unsupported file format: {ext}')

    @transaction.atomic
    def import_csv(self, file_path):
        """Import data from CSV file
        Format: poi_id, poi_name, poi_latitude, poi_longitude, poi_category, poi_ratings
        """
        imported_count = 0
        
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                try:
                    # Parse ratings (assuming comma-separated values in brackets or similar)
                    ratings_str = row.get('poi_ratings', '').strip()
                    ratings = self.parse_ratings(ratings_str)
                    
                    poi = PointOfInterest(
                        external_id=row['poi_id'],
                        name=row['poi_name'],
                        latitude=Decimal(row['poi_latitude']),
                        longitude=Decimal(row['poi_longitude']),
                        category=row['poi_category'],
                        ratings_data=ratings
                    )
                    poi.save()
                    imported_count += 1
                    
                except (KeyError, ValueError, InvalidOperation) as e:
                    self.stdout.write(
                        self.style.WARNING(f'Skipping invalid CSV row: {row}. Error: {e}')
                    )
                    continue
        
        return imported_count

    @transaction.atomic
    def import_json(self, file_path):
        """Import data from JSON file
        Format: id, name, coordinates[latitude, longitude], category, ratings, description
        """
        imported_count = 0
        
        with open(file_path, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            
            # Handle both single object and array of objects
            if isinstance(data, dict):
                data = [data]
            
            for item in data:
                try:
                    coordinates = item.get('coordinates', {})
                    ratings = item.get('ratings', [])
                    
                    poi = PointOfInterest(
                        external_id=str(item['id']),
                        name=item['name'],
                        latitude=Decimal(str(coordinates['latitude'])),
                        longitude=Decimal(str(coordinates['longitude'])),
                        category=item['category'],
                        ratings_data=ratings,
                        description=item.get('description', '')
                    )
                    poi.save()
                    imported_count += 1
                    
                except (KeyError, ValueError, InvalidOperation) as e:
                    self.stdout.write(
                        self.style.WARNING(f'Skipping invalid JSON item: {item}. Error: {e}')
                    )
                    continue
        
        return imported_count

    @transaction.atomic
    def import_xml(self, file_path):
        """Import data from XML file
        Format: pid, pname, platitude, plongitude, pcategory, pratings
        """
        imported_count = 0
        
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Handle different possible XML structures
        poi_elements = root.findall('.//poi') or root.findall('.//point_of_interest') or [root]
        
        for poi_elem in poi_elements:
            try:
                # Try to find elements with different possible tag names
                pid = self.get_xml_text(poi_elem, ['pid', 'id', 'poi_id'])
                pname = self.get_xml_text(poi_elem, ['pname', 'name', 'poi_name'])
                platitude = self.get_xml_text(poi_elem, ['platitude', 'latitude', 'poi_latitude'])
                plongitude = self.get_xml_text(poi_elem, ['plongitude', 'longitude', 'poi_longitude'])
                pcategory = self.get_xml_text(poi_elem, ['pcategory', 'category', 'poi_category'])
                pratings = self.get_xml_text(poi_elem, ['pratings', 'ratings', 'poi_ratings'])
                
                if not all([pid, pname, platitude, plongitude, pcategory]):
                    continue
                
                ratings = self.parse_ratings(pratings or '')
                
                poi = PointOfInterest(
                    external_id=pid,
                    name=pname,
                    latitude=Decimal(platitude),
                    longitude=Decimal(plongitude),
                    category=pcategory,
                    ratings_data=ratings
                )
                poi.save()
                imported_count += 1
                
            except (ValueError, InvalidOperation) as e:
                self.stdout.write(
                    self.style.WARNING(f'Skipping invalid XML element. Error: {e}')
                )
                continue
        
        return imported_count

    def get_xml_text(self, element, tag_names):
        """Get text from XML element trying multiple possible tag names"""
        for tag_name in tag_names:
            elem = element.find(tag_name)
            if elem is not None and elem.text:
                return elem.text.strip()
        return None

    def parse_ratings(self, ratings_str):
        """Parse ratings string into a list of floats"""
        if not ratings_str:
            return []
        
        # Remove brackets and split by comma
        ratings_str = ratings_str.strip('[](){}')
        if not ratings_str:
            return []
        
        ratings = []
        for rating in ratings_str.split(','):
            try:
                rating = rating.strip()
                if rating:
                    ratings.append(float(rating))
            except ValueError:
                continue
        
        return ratings