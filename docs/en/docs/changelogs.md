## 0.3.0
### Features
- Add `Date` scalar
- Add parser for the `DateTime` scalar
- Add `include`, `exclude` and `fields` settings when generating Pydantic models
- Make error field configurable in settings

### Fixes
- Fix `.env` path in `settings.py` generared by `turb project`
- Fix error when declaring validators on generated Pydantic models

### Changes
- The GraphQL config for `GraphQLModel` now must be declared in `GraphQL` inner class
- Rename `#!python @scope` decorator to `#!python @policy`
- Raise `SchemaError` if `#!python @policy` is used on a non-nullable field

### Docs
- Improve Quick Start

### Internal
- Update dev dependencies
- Make the project structure less nested
- Remove `camel_to_snake` util and use `convert_camel_case_to_snake` from Ariadne instead


## 0.2.0

### Features
- Generate Pydantic models from schema
- Policy based access control (PBAC)
- Add fresh token
- Add Turbulette CLI `turb`
- Add CRUD role methods on auth user model
- Add [async-caches](https://github.com/rafalp/async-caches)
- Add csrf middleware
- Add ariadne extensions through settings
- Add `set_password()` to AbtractUser
- Allow to start a project with no database connection
### Fixes
- Fix error when no routes was defined
- More consistent error codes
- Add mypy and black checks
### Docs
- Add quickstart documentation
### CI
- Move from Travis CI to Github Action
- Add pre-commit hooks
- Add mypy and black formatting checks in test workflow
