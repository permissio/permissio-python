# Changelog

All notable changes to the Permis.io Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial SDK implementation
- Permission checking with `check()` method
- Async support with `check_async()` method
- Auto-scope detection from API key
- Full CRUD operations for Users, Roles, Tenants, and Resources
- FastAPI and Flask middleware integration
- Type hints throughout
- Comprehensive examples

## [0.1.0] - 2024-XX-XX

### Added
- Initial release
- `Permisio` client class
- `PermisioConfig` for configuration
- `User` and `Resource` builders for building check requests
- API clients for Users, Roles, Tenants, Resources, and Role Assignments
- FastAPI middleware for permission enforcement
- Full type hints and documentation
- Examples for common use cases
