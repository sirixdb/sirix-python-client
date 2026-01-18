# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

sirix-python-client is a Python SDK for SirixDB, a temporal versioned NoSQL database. It supports both synchronous and asynchronous operations and includes a CLI shell interface.

## Build and Development Commands

```bash
# Install all dependencies (runtime + dev + docs)
pip install -r requirements-all.txt

# Install in development mode
pip install -e .

# Run tests (requires Docker services running)
python -m pytest --cov=pysirix --cov-config=.coveragerc -v -s

# Run a single test file
python -m pytest tests/test_sirix_sync.py -v -s

# Run a single test
python -m pytest tests/test_sirix_sync.py::test_function_name -v -s

# Start test infrastructure (Keycloak + SirixDB)
bash test.sh

# Build documentation
cd docs && make html
```

## Test Infrastructure

Tests require Docker Compose services (Keycloak for auth, SirixDB server):
- `tests/resources/docker-compose.yml` - Service definitions
- Keycloak runs on port 8080
- SirixDB runs on port 9443
- Run `bash test.sh` to start services before running tests

## Architecture

### Dual Sync/Async Pattern
The library provides identical interfaces for sync and async code:
- `sirix_sync(username, password, client: httpx.Client)` → synchronous operations
- `sirix_async(username, password, client: httpx.AsyncClient)` → async/await operations
- Both use the same underlying `Sirix` class, which detects the client type and instantiates `SyncClient` or `AsyncClient`

### Three-Level Resource Hierarchy
1. **Sirix** (`sirix.py`) - Server-level orchestrator: access databases, execute global queries
2. **Database** (`database.py`) - Database-level: create/delete databases, access resources
3. **Resource** (`resource.py`) - Resource-level: CRUD operations on JSON/XML documents

### Two-Tier API
- **High-level**: `JsonStoreSync`/`JsonStoreAsync` (`json_store.py`) - MongoDB-like interface with `insert()`, `find()`, `update()`, `delete()`
- **Low-level**: `SyncClient`/`AsyncClient` (`sync_client.py`, `async_client.py`) - Direct HTTP endpoint wrappers

### Key Files
- `pysirix/__init__.py` - Entry points and public API exports
- `pysirix/auth.py` - Keycloak OAuth2 authentication with automatic token refresh
- `pysirix/errors.py` - `SirixServerError` exception and `include_response_text_in_errors()` context manager
- `pysirix/types.py` - TypedDict definitions for API responses
- `pysirix/constants.py` - Enums: `DBType`, `Insert`, `TimeAxisShift`

### CLI Shell
- Entry point: `pysirix` command (configured in setup.py)
- Implementation: `pysirix/shell/sirixsh.py`
- Config file: `~/.pysirix-shell/config.json`

## Conventions

- Python 3.9+ required
- Uses httpx (0.21-0.24) for HTTP client
- Conventional commits: `feat:`, `fix:`, etc.
- Test files mirror source structure: `test_sirix_sync.py`, `test_sirix_async.py`, etc.
