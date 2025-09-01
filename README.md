# Points of Interest (PoI) Management System

A Django web application for managing Points of Interest with data import capabilities from CSV, JSON, and XML files.

## Features

- **Multi-format Data Import**: Import PoI data from CSV, JSON, and XML files
- **Django Admin Interface**: Full-featured admin interface with search and filtering
- **Database Management**: Automatic calculation of average ratings
- **Search Functionality**: Search by internal ID or external ID
- **Category Filtering**: Filter PoIs by category
- **Data Validation**: Robust error handling during import

## Requirements

- Python 3.10 or above
- Django 5.2.5
- SQLite (default database)

## Installation

1. **Clone or download the project**:
   ```bash
   cd poi_project
   ```

2. **Install dependencies**:
   ```bash
   pip install django
   ```

3. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser for admin access**:
   ```bash
   python manage.py createsuperuser
   ```

## Usage

### Starting the Development Server

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000/`

### Importing Data

Use the management command to import PoI data from files:

```bash
python manage.py import_poi path/to/your/file.csv
python manage.py import_poi path/to/your/file.json
python manage.py import_poi path/to/your/file.xml
```

You can also import multiple files at once:
```bash
python manage.py import_poi file1.csv file2.json file3.xml
```

### File Formats

#### CSV Format
```csv
poi_id,poi_name,poi_latitude,poi_longitude,poi_category,poi_ratings
POI001,Central Park,40.7829,-73.9654,Park,"[4.5, 4.2, 4.8, 4.1, 4.6]"
```

#### JSON Format
```json
{
  "id": "JSON001",
  "name": "Statue of Liberty",
  "coordinates": {
    "latitude": 40.6892,
    "longitude": -74.0445
  },
  "category": "Monument",
  "ratings": [4.8, 4.9, 4.7, 4.6, 4.8],
  "description": "Iconic symbol of freedom"
}
```

#### XML Format
```xml
<poi>
  <pid>XML001</pid>
  <pname>Empire State Building</pname>
  <platitude>40.7484</platitude>
  <plongitude>-74.0048</plongitude>
  <pcategory>Skyscraper</pcategory>
  <pratings>4.5,4.7,4.3,4.8,4.2</pratings>
</poi>
```

### Admin Interface

Access the Django admin interface at `http://localhost:8000/admin/`

**Features:**
- View all PoIs with internal ID, name, external ID, category, and average rating
- Search by internal ID or external ID
- Filter by category
- Sort by any column
- Add, edit, and delete PoIs

## Database Schema

The `PointOfInterest` model includes:
- `internal_id`: Auto-generated primary key
- `external_id`: External identifier from source files
- `name`: PoI name
- `coordinates`: JSON field storing latitude/longitude
- `category`: PoI category
- `ratings_data`: JSON field storing individual ratings
- `avg_rating`: Automatically calculated average rating
- `description`: Optional description field
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

## Sample Data

The project includes sample data files in the `sample_data/` directory:
- `sample_pois.csv`: 5 sample PoIs in CSV format
- `sample_pois.json`: 3 sample PoIs in JSON format  
- `sample_pois.xml`: 4 sample PoIs in XML format

To import all sample data:
```bash
python manage.py import_poi sample_data/sample_pois.csv sample_data/sample_pois.json sample_data/sample_pois.xml
```

## Architecture Decisions

### Data Storage
- **Ratings**: Stored as JSON arrays to preserve individual rating values while calculating averages
- **Coordinates**: Stored as JSON objects for flexibility and easy access to lat/lng
- **Average Rating**: Calculated automatically and stored for performance

### Import Strategy
- **Error Handling**: Continues processing other records if one fails
- **Duplicate Prevention**: Uses external_id as unique identifier
- **Format Detection**: Automatically detects file format based on extension
- **Validation**: Validates required fields and data types

### Admin Interface
- **Search Fields**: Both internal and external IDs for maximum flexibility
- **Filters**: Category and rating-based filtering
- **Display**: Shows all required fields plus additional useful information

## Assumptions Made

1. **Ratings Format**: 
   - CSV: JSON array string format
   - JSON: Array of numbers
   - XML: Comma-separated values

2. **Coordinates**:
   - Always provided as latitude/longitude pairs
   - Stored with high precision (7 decimal places)

3. **External IDs**:
   - Should be unique across all imported data
   - Used to prevent duplicate imports

4. **Categories**:
   - Free-form text field
   - No predefined category list

## Potential Improvements

1. **API Development**: Add REST API endpoints for programmatic access
2. **Bulk Operations**: Add bulk import/export functionality in admin
3. **Data Validation**: Add more sophisticated validation rules
4. **Caching**: Implement caching for frequently accessed data
5. **Geospatial Features**: Add map visualization and distance calculations
6. **User Management**: Add role-based access control
7. **Import History**: Track import operations and provide rollback functionality
8. **File Upload Interface**: Web-based file upload instead of command-line only
9. **Data Export**: Export functionality in multiple formats
10. **Performance**: Add database indexing for large datasets

## Testing

The application has been tested with:
- Sample data import from all three formats
- Admin interface functionality
- Search and filtering operations
- Error handling for malformed data
>>>>>>> 8778e0e (Initial commit)
