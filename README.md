# Turbulette

[![CI](https://github.com/turbulette/turbulette/workflows/CI/badge.svg)](https://github.com/turbulette/turbulette/actions?query=workflow%3ACI)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/e244bb031e044079af419dabd40bb7fc)](https://www.codacy.com/gh/python-turbulette/turbulette/dashboard?utm_source=github.com&utm_medium=referral&utm_content=python-turbulette/turbulette&utm_campaign=Badge_Coverage)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/e244bb031e044079af419dabd40bb7fc)](https://www.codacy.com/gh/python-turbulette/turbulette/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=python-turbulette/turbulette&amp;utm_campaign=Badge_Grade)
![PyPI](https://img.shields.io/pypi/v/turbulette)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/turbulette)
![PyPI - License](https://img.shields.io/pypi/l/Turbulette)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Generic badge](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Generic badge](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit) [![Join the chat at https://gitter.im/turbulette/turbulette](https://badges.gitter.im/turbulette/turbulette.svg)](https://gitter.im/turbulette/turbulette?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

<p align="center">Turbulette packages all you need to build great GraphQL APIs :</p>

<p align="center"><strong><em>ASGI framework, GraphQL library, ORM and data validation</em></strong></p>

---

Documentation : [https://turbulette.github.io/turbulette/](https://turbulette.github.io/turbulette/)

---

Features :

- Split your API in small, independent applications
- Generate Pydantic models from GraphQL types
- JWT authentication with refresh and fresh tokens
- Declarative, powerful and extendable policy-based access control (PBAC)
- Extendable auth user model with role management
- Async caching (provided by async-caches)
- Built-in CLI to manage project, apps, and DB migrations
- Built-in pytest plugin to quickly test your resolvers
- Settings management at project and app-level (thanks to simple-settings)
- CSRF middleware
- 100% test coverage
- 100% typed, your IDE will thank you ;)
- Handcrafted with ❤️, from 🇫🇷

## Requirements

Python 3.6+

👍 Turbulette makes use of great tools/frameworks and wouldn't exist without them :

- [Ariadne](https://ariadnegraphql.org/) - Schema-first GraphQL library
- [Starlette](https://www.starlette.io/) - The little ASGI framework that shines
- [GINO](https://python-gino.org/docs/en/master/index.html) - Lightweight, async ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Powerful data validation with type annotations
- [Alembic](https://alembic.sqlalchemy.org/en/latest/index.html) - Lightweight database migration tool
- [simple-settings](https://github.com/drgarcia1986/simple-settings) - A generic settings system inspired by Django's one
- [async-caches](https://github.com/rafalp/async-caches) - Async caching library
- [Click](https://palletsprojects.com/p/click/) - A "Command Line Interface Creation Kit"

## Installation

``` bash
pip install turbulette
```

You will also need an ASGI server, such as [uvicorn](https://www.uvicorn.org/) :

``` bash
pip install uvicorn
```

----

## 🚀 Quick Start

Here is a short example that demonstrates a minimal project setup.

We will see how to scaffold a simple Turbulette project, create a Turbulette application, and write some GraphQL schema/resolver. It's advisable to start the project in a virtualenv to isolate your dependencies.
Here we will be using [poetry](https://python-poetry.org/) :

``` bash
poetry init
```

Then, install Turbulette from PyPI :

``` bash
poetry add turbulette
```

For the rest of the tutorial, we will assume that commands will be executed under the virtualenv. To spawn a  shell inside the virtualenv, run :

```bash
poetry shell
```

### 1: Create a project

First, create a directory that will contain the whole project.

Now, inside this folder, create your Turbulette project using the `turb` CLI :

``` bash
turb project eshop
```

You should get with something like this :

```console
.
└── 📁 eshop
    ├── 📁 alembic
    │   ├── 📄 env.py
    │   └── 📄 script.py.mako
    ├── 📄 .env
    ├── 📄 alembic.ini
    ├── 📄 app.py
    └── 📄 settings.py
```

Let's break down the structure :

- `📁 eshop` : Here is the so-called *Turbulette project* folder, it will contain applications and project-level configuration files
- `📁 alembic` : Contains the [Alembic](https://alembic.sqlalchemy.org/en/latest/) scripts used when generating/applying DB migrations
  - `📄 env.py`
  - `📄 script.py.mako`
- `📄 .env` : The actual project settings live here
- `📄 app.py` : Your API entrypoint, it contains the ASGI app
- `📄 settings.py` : Will load settings from `.env` file


Why have both `.env` and `settings.py`?

You don't *have to*. You can also put all your settings in `settings.py`.
But Turbulette encourage you to follow the [twelve-factor methodology](https://12factor.net),
that recommend to separate settings from code because config varies substantially across deploys, *code does not*.
This way, you can untrack `.env` from version control and only keep tracking `settings.py`, which will load settings
from `.env` using Starlette's `Config` object.

### 2: Create the first app

Now it's time to create a Turbulette application!

Run this command under the project directory (`eshop`) :

```bash
turb app --name account
```

You need to run `turb app` under the project dir because the CLI needs to access the `almebic.ini` file to create the initial database migration.

You should see your new app under the project folder :

```console
.
└── 📁 eshop
    ...
    |
    └── 📁 account
        ├── 📁 graphql
        ├── 📁 migrations
        │   └── 📄 20200926_1508_auto_ef7704f9741f_initial.py
        ├── 📁 resolvers
        └── 📄 models.py
```

Details :

- `📁 graphql` : All the GraphQL schema will live here
- `📁 migrations` : Will contain database migrations generated by Alembic
- `📁 resolvers` : Python package where you will write resolvers binded to the schema
- `📄 models.py` : Will hold GINO models for this app

What is this "initial" python file under `📁 migrations`?

We won't cover database connection in this quickstart, but note that it's the initial database migration
for the `account` app that creates its dedicated Alembic branch, needed to generate/apply per-app migrations.

Before writing some code, the only thing to do is make Turbulette aware of our lovely account app.

To do this, open `📄 eshop/settings.py` and add `"eshop.account"` to `INSTALLED_APPS`,
so the application is registered and can be picked up by Turbulette at startup :

``` python
# List installed Turbulette apps that defines some GraphQL schema
INSTALLED_APPS = ["eshop.account"]
```

### 3: GraphQL schema

Now that we have our project scaffold, we can start writing actual schema/code.

Create a `schema.gql` file in the `📁 graphql` folder and add this base schema :

``` graphql
extend type Mutation {
    registerCard(input: CreditCard!): SuccessOut!
}

input CreditCard {
    number: String!
    expiration: Date!
    name: String!
}

type SuccessOut {
    success: Boolean
    errors: [String]
}

```

Note that we *extend* the type `Mutation` because Turbulette already defines it. The same goes for `Query` type

Notice that with use the `Date` scalar, it's one of the custom scalars provided by Turbulette. It parses string in the ISO8601 date format YYY-MM-DD.

### 4: Add pydantic model

We want to validate our `CreditCard` input to ensure the user has entered a valid card number and date.
Fortunately, Turbulette integrates with [Pydantic](https://pydantic-docs.helpmanual.io/), a data validation library that uses python type annotations,
and offers a convenient way to generate a Pydantic model from a schema type.

Create a new `📄 pyd_models.py` under `📁 account` :

```python
from turbulette.validation import GraphQLModel
from pydantic import PaymentCardNumber


class CreditCard(GraphQLModel):
    class GraphQL:
        gql_type = "CreditCard"
        fields = {"number": PaymentCardNumber}
```

What's happening here?

The inherited `GraphQLModel` class is a pydantic model that knows about the GraphQL schema and can produce pydantic fields from a given GraphQL type. We specify the GraphQL type with the `gql_type` attribute; it's the only one required.

But we also add a `fields` attribute to override the type of `number` field because it is string typed in our schema. If we don't add this, Turbulette will assume that `number` is a string and will annotate the number field as `str`.
`fields` is a mapping between GraphQL field names and the type that will override the schema's one.

Let's add another validation check: the expiration date. We want to ensure the user has entered a valid date (i.e., at least greater than now) :

```python hl_lines="3 11 12 13 14 15"
from datetime import datetime
from pydantic import PaymentCardNumber
from turbulette.validation import GraphQLModel, validator


class CreditCard(GraphQLModel):
    class GraphQL:
        gql_type = "CreditCard"
        fields = {"number": PaymentCardNumber}

    @validator("expiration")
    def check_expiration_date(cls, value):
        if value < datetime.now():
            raise ValueError("Expiration date is invalid")
        return value
```

Why don't we use the `@validator` from Pydantic?

For those who have already used Pydantic, you probably know about the `@validator` decorator used add custom validation rules on fields.

But here, we use a `@validator` imported from `turbulette.validation`, why?

They're almost identical. Turbulette's validator is just a shortcut to the Pydantic one with `check_fields=False` as a default, instead of `True`, because we use an inherited `BaseModel`. The above snippet would correctly work if we used Pydantic's validator and explicitly set `@validator("expiration", check_fields=False)`.

### 5: Add a resolver

The last missing piece is the resolver for our `user` mutation, to make the API returning something when querying for it.

The GraphQL part is handled by [Ariadne](https://ariadnegraphql.org/), a schema-first GraphQL library that allows binding the logic to the schema with minimal code.

As you may have guessed, we will create a new Python module in our `📁 resolvers` package.

Let's call it `📄 user.py` :

``` python
from turbulette import mutation
from ..pyd_models import CreditCard

@mutation.field("registerCard")
async def register(obj, info, valid_input, **kwargs):
    return {"success": True}
```

`mutation` is the base mutation type defined by Turbulette and is used to register all mutation resolvers (hence the use of `extend type Mutation` on the schema).
For now, our resolver is very simple and doesn't do any data validation on inputs and doesn't handle errors.

Turbulette has a `@validate` decorator that can be used to validate resolver input using a pydantic model (like the one defined in [Step 4](#4-add-pydantic-model)).

Here's how to use it:

``` python hl_lines="3 6 7"
from turbulette import mutation
from ..pyd_models import CreditCard
from turbulette.validation import validate

@mutation.field("registerCard")
@validate(CreditCard)
async def register(obj, info, valid_input, **kwargs):
    return {"success": True}
```

Note the new `valid_input` param. The `@validate` decorator produces it if the validation succeeds.
But what happens otherwise? Normally, if the validation fails, pydantic will raise a `ValidationError`,
but here the `@validate` decorator handles the exception and will add error messages returned by pydantic into a dedicated error field in the GraphQL response.

### 5: Run it

Our `user` mutation is now binded to the schema, so let's test it.

Start the server in the root directory (the one containing `📁 eshop` folder) :

```bash
uvicorn eshop.app:app --port 8000
```

Now, go to [http://localhost:8000/graphql](http://localhost:8000/graphql), you will see the [GraphQL Playground](https://github.com/graphql/graphql-playground) IDE.
Finally, run the user mutation, for example :

``` graphql
mutation card {
  registerCard(
    input: {
      number: "4000000000000002"
      expiration: "2023-05-12"
      name: "John Doe"
    }
  ) {
    success
    errors
  }
}
```

Should give you the following expected result :

``` json
{
  "data": {
    "registerCard": {
      "success": true,
      "errors": null
    }
  }
}
```

Now, try entering a wrong date (before *now*). You should see the validation error as expected:

```json
{
  "data": {
    "registerCard": {
      "success": null,
      "errors": [
        "expiration: Expiration date is invalid"
      ]
    }
  }
}
```

How the error message end in the `errors` key?

Indeed, we didn't specify anywhere that validation errors should be passed to the `errors` key in our `SuccessOut` GraphQL type.
That is because Turbulette has a setting called `ERROR_FIELD`, which defaults to `"errors"`.
This setting indicates the error field on the GraphLQ output type used by Turbulette when collecting query errors.

It means that if you didn't specify `ERROR_FIELD` on the GraphQL type, you would get an exception telling you that the field is missing.

It's the default (and recommended) way of handling errors in Turbulette. Still, as all happens in the `@validate`, you can always remove it and manually instantiate your Pydantic models in resolvers.

Good job! 👏

That was a straightforward example, showing off a simple Turbulette API set up. To get the most of it, follow the  [User Guide](https://python-turbulette.github.io/turbulette/user-guide/) .
