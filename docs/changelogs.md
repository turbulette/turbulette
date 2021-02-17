## 0.5.1 (2021-02-18)
### Changes
- JWT claims has been moved to `info.context["claims"]` when requiring using auth directive
- Add `VALIDATION_KWARG_NAME` settings, default to `"_val_data"`

### Internals
- Update linting configuration
- Add a documented makefile
- Add a [code of conduct](https://github.com/turbulette/turbulette/blob/main/CODE_OF_CONDUCT.md)

### Docs
- Use netlify for deploys
- Add [termynal](https://github.com/ines/termynal) to prettify terminal commands


## 0.5.0 (2021-02-04)
### Features
- Add `createuser` command to turb CLI
- Add support for python 3.9

### Fixes
- Update error messages on pydantic bindings

### Docs
- Add user guide and reference


## 0.4.0 (2020-10-24)
### Features
- Add subscription type and websocket route

## 0.3.1
### Fixes
- Fix `upgrade` and `makerevision` CLI commands

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
