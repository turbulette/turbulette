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
