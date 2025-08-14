# MCP Query API

A FastAPI-based application that handles natural language queries for product recommendations and student information.

## Features

- Natural language query processing
- Product recommendations for CSE, ECE, and MECH departments
- Student information retrieval
- Robust error handling
- Database connection management
- Automatic database setup with sample data

## Quick Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Update the `.env` file with your MySQL credentials:
   ```
   MYSQL_USER=your_mysql_username
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   DATABASE_TIMEOUT=10
   ```

3. **Set up databases (Optional):**
   ```bash
   python setup_database.py
   ```
   This will create the required databases and tables with sample data.

## Running the Application

```bash
python run.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `POST /ask` - Submit a natural language query
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation

## Example Queries

- "Show me CSE products"
- "What ECE products do you have?"
- "List all students"
- "Show students in the university"

## Database Schema

### Sales Database
- **products** table: `id`, `name`, `ideal_for`, `created_at`

### University Database
- **students** table: `id`, `name`, `department`, `year`, `created_at`

## Error Handling

The application includes comprehensive error handling for:
- Database connection failures
- Invalid queries
- Missing environment variables
- SQL execution errors
- Connection timeouts

## Development

- The application uses connection pooling and timeouts for better performance
- All database operations are wrapped in try-catch blocks
- Input validation is implemented for all API endpoints 