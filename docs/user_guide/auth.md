Turbulette gives you JWT authentication through the integrated auth app.

## JSON Web Token

But what's actually *JWT?*

From [jwt.io](https://jwt.io/introduction/):

> JSON Web Token (JWT) is an open standard [RFC 7519](https://tools.ietf.org/html/rfc7519) that defines a compact and self-contained way for securely transmitting information between parties as a JSON object. This information can be verified and trusted because it is digitally signed.

One important thing to note is that JWTs are *digitally signed*, but they are *not encrypted*. It means that anyone can see what's in the token,
but no one can modify it because the signature would be invalid.

A encoded JWT looks like this:

```console
eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJodHRwOi8vYXBpLmlvL2Jvb2tpbmciLCJleHAiOjE2MDU5MTExMjMsImlhdCI6MTYwNTkxMDgyMywiaXNzIjoiaHR0cDovL2FwaS5pby9hdXRoLyIsImp0aSI6ImRnTm85eF9UbEN6RHVUQmdDRGxSSlEiLCJuYmYiOjE2MDU5MTA4MjMsInNjb3BlcyI6WyJfc3RhZmYiXSwic3ViIjoiZWxzYSIsInR5cGUiOiJhY2Nlc3MifQ.9XXOqhcj_icb_vGm0AWj6VkjiEV1E8dfXK7ef9j1fZniUJ3K02lKwo5GbSQMPJYrrpr9LBy9Y94YKfTDDrJzaA
```

But once decoded here is what's inside:

```json
{
  "aud": "http://api.io/booking",
  "exp": 1605911123,
  "iat": 1605910823,
  "iss": "http://api.io/auth/",
  "jti": "dgNo9x_TlCzDuTBgCDlRJQ",
  "nbf": 1605910823,
  "scopes": [
    "_staff"
  ],
  "sub": "elsa",
  "type": "access"
}
```

Each key in this dictionary is called a "claim". A claim can be any piece of information documenting *who* is the user (the one owning the token).

A claim can be of two types: **Reserved** or **Custom**.

A reserved claim is one of those defined by RFC 7519:

- `iss`: Issuer. Identifies who issued the JWT.
- `sub`: Subject. Identifies who is the subject of the JWT.
- `aud`: Audience. Identifies the JWT recipients (those for whom the token is intended).
- `iat`: Issued at. The time at which the JWT was issued.
- `exp`: Expiration time. The after which the JWT is expired (cannot be used for processing any request).
- `nbf`: Not before time. The time before which the JWT cannot be accepted for processing.
- `jti`: JWT id. A unique identifier for the JWT.

A custom claim is simply one that is not reserved. The auth app defines two custom claims:

- `scope`: User permissions and/or roles.
- `type`: The type of the token (can be either `access` or `refresh`)

The main advantage of JWTs is their *stateless* nature. It's stateless because the API does not need anyone to know if the token is valid or not, it just has to check the token signature and expiration time. In a stateful world, a so called bearer token is usually used to retrieve a specific user and all of its belonging information, but this implies querying a source of truth (e.g: a database). With JWTs, this does not happens because all you need is *self-contained* in the token.

For more details on JWT, check [jwt.io](https://jwt.io/introduction/) and the [RFC 7519](https://tools.ietf.org/html/rfc7519)

## Auth user model

### Enable the auth app

The very first step to add authentication to your API is to enable the auth app:


=== ".env"

    ``` bash
    INSTALLED_APPS=turbulette.apps.auth,my_project.my_app
    ```

=== "settings.py"

    ``` python
    from starlette.datastructures import CommaSeparatedStrings

    ...

    INSTALLED_APPS = config("INSTALLED_APPS", cast=CommaSeparatedStrings, default=[])
    ```

### Subclass `AbstractUser`

Then, you have to subclass the `AbstractUser` model:

``` python
# models.py

from turbulette.db import Model
from turbulette.apps.auth.models import AbstractUser


class User(AbstractUser, Model):
  pass
```
The User model also has to inherit `Model` because `AbstractUser` acts as a mixer class here: it's a bare python class providing necessary columns the auth app needs to manage authentication. See the [AbstractUser](/reference/apps/auth/models/#turbulette.apps.auth.models.AbstractUser) reference for more details.

Also, it's better to inherit `AbstractUser` before `Model`to benefit from all features from `AbstractUser`.

!!! info
    Of course, you can add additional columns to suit your needs, just keep in mind that your user model *must* extend `AbstractUser`.

Then, set the `AUTH_USER_MODEL` setting:

=== ".env"

    ``` bash
    AUTH_USER_MODEL=my_project.my_app.models.User
    ```

=== "settings.py"

    ``` python
    AUTH_USER_MODEL = config("AUTH_USER_MODEL", cast=str, default=None)
    ```

As the name suggests, it's the model used to store users and authenticate them.
