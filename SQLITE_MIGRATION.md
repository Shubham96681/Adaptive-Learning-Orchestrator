# SQLite Database Migration

## Overview

The system has been migrated from in-memory storage to **SQLite database** for persistent data storage.

## What Changed

### Before (In-Memory)
- Problems stored in Python dictionary
- Data lost on server restart
- Fast but not persistent

### After (SQLite)
- Problems stored in SQLite database (`problems.db`)
- Data persists across restarts
- Indexed queries for performance
- Production-ready storage solution

## Database Schema

```sql
CREATE TABLE problems (
    id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    topic TEXT NOT NULL,
    difficulty INTEGER NOT NULL CHECK (difficulty >= 1 AND difficulty <= 5),
    estimated_time_to_solve_minutes INTEGER NOT NULL CHECK (estimated_time_to_solve_minutes > 0)
);

-- Indexes for performance
CREATE INDEX idx_topic_difficulty ON problems(topic, difficulty);
CREATE INDEX idx_topic ON problems(topic);
```

## New Files

1. **`app/services/database.py`**
   - Database connection management
   - Schema initialization
   - Query execution helpers

2. **Updated `app/services/problem_service.py`**
   - Now uses SQLite instead of in-memory dict
   - All methods updated to use SQL queries
   - Maintains same interface (no breaking changes)

## Benefits

✅ **Persistence**: Data survives server restarts
✅ **Performance**: Indexed queries are fast
✅ **Scalability**: Can handle larger datasets
✅ **Production-Ready**: SQLite is battle-tested
✅ **No External Dependencies**: SQLite is built into Python

## How It Works

1. **On First Run**: Database is created automatically
2. **On Startup**: If database is empty, loads problems from JSON file
3. **Queries**: All queries use indexed SQL for fast lookups
4. **Transactions**: Updates use transactions for data integrity

## Database Location

The database file `problems.db` is created in the project root directory.

## Migration Notes

- **No Breaking Changes**: All API endpoints work the same
- **Automatic Migration**: Existing JSON data is loaded on first run
- **Backward Compatible**: Can still load from JSON via `/api/problems/load`

## Testing

Run the test script to verify everything works:
```bash
python test_api.py
```

The database will be created automatically on first run.

