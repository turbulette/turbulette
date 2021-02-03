from datetime import timedelta
from typing import List, Optional


SETTINGS_RULES = {
    "REQUIRED_SETTINGS": ["AUTH_USER_MODEL", "SECRET_KEY"],
    "REQUIRED_SETTINGS_TYPES": {
        "JWT_ALGORITHM": "str",
        "JWT_AUDIENCE": "str",
        "JWT_ISSUER": "str",
        "JWT_PREFIX": "str",
        "JWT_VERIFY": "bool",
        "JWT_JTI_SIZE": "int",
        "JWT_VERIFY_EXPIRATION": "bool",
        "JWT_REFRESH_ENABLED": "bool",
        "JWT_BLACKLIST_ENABLED": "bool",
    },
}

HASH_ALGORITHM: str = "bcrypt"
"""
Defines the hash algorithm used to hash user passwords

Default: `bcrypt`
"""

TURBULETTE_ERROR_KEY: str = "errors"
"""
The key holding Turbulette errors under `"extensions"` in GraphQL responses.

Defaults: `"errors"`
"""

# JWT
JWT_VERIFY: bool = True
"""Enables JWT verification.

When `False`, the token will be parsed (so claims can be accessed),
but signature and expiration won't be verified.

Default: `True`
"""

JWT_VERIFY_EXPIRATION: bool = True
"""Enables token expiration check.

When `False`, the token will be parsed and signature verified, but
expiration won't be.

Default: `True`
"""

JWT_PREFIX: str = "JWT"
"""
Set the prefix string that must precede the JWT in the `AUTHORIZATION` header.

Default: `"JWT"`
"""

JWT_EXPIRATION_DELTA: timedelta = timedelta(seconds=60 * 5)
"""Set the expiration period of JWTs.

Default: `timedelta(seconds=60 * 5)`
"""

JWT_REFRESH_EXPIRATION_DELTA: timedelta = timedelta(days=7)
"""Set the expiration period for refresh JWTs.

Default: `timedelta(days=7)`
"""

JWT_FRESH_DELTA: timedelta = timedelta(seconds=15)
"""Set the expiration period for access token "freshness".

Default: `timedelta(seconds=15)`
"""

JWT_REFRESH_ENABLED: bool = True
"""Enables refresh tokens

Default: `True`
"""

JWT_AUDIENCE: Optional[str] = None
"""Sets the `aud` claims.

Default: `None`
"""

JWT_ISSUER: Optional[str] = None
"""Sets the `iss` claims

Default: None
"""

JWT_LEEWAY: timedelta = timedelta(0)
"""The amount of leeway to allow between the issuer's clock
and the verifier's clock when verifiying that the token was generated in the past.

Default: `timedelta(0)` (no leeway)
"""

JWT_BLACKLIST_ENABLED: bool = False
"""Enables token blacklist.

Default: `False`

!!! warning
    Token blacklist is not implemented yet, setting this to `True` will have no effect.
"""

JWT_BLACKLIST_TOKEN_CHECKS: List[str] = ["access", "refresh"]
"""Set which type of tokens can be blacklisted.

!!! warning
    Token blacklist is not implemented yet, this setting have no effect.
"""

JWT_JTI_SIZE: int = 16
"""Set the JWT ID (`jti`) size.

Default: `16`

!!! warning
    JWT IDs are currently not enabled when encoding tokens
"""

JWT_ALGORITHM: str = "ES256"
"""Algorithm to use for generating signature.

Default: `"ES256"`

Available values are :
`RS256`, `RS384`, `RS512`, `PS256`, `PS384`, `PS512`,
`ES256`, `ES384`, `ES512`, `HS256`, `HS384`, `HS512`
"""

JWT_ENCRYPT: bool = False
"""Enables tokens encryption.

Default: `False`
"""

JWE_ALGORITHM: str = "A256KW"
"""Specifies the algorithm used to encrypt the content encryption key (CEK).

Default: `"A256KW"`

Valid key management algorithms are:

`RSA1_5`, `RSA-OAEP`, `RSA-OAEP-256`,
`A128KW`, `A192KW`, `A256KW`,
`dir`,
`ECDH-ES`, `ECDH-ES+A128KW`, `ECDH-ES+A192KW`, `ECDH-ES+A256KW`,
`A128GCMKW`, `A192GCMKW`, `A256GCMKW`,
`PBES2-HS256+A128KW`, `PBES2-HS384+A192KW`, `PBES2-HS512+A256KW`,
"""

JWE_ENCRYPTION: str = "A256CBC-HS512"
"""Specifies the algorithm used to encrypt the JWT.

Default: `"A256CBC-HS512"`

Valid content encryption algorithms are:

`A128CBC-HS256`, `A192CBC-HS384`, `A256CBC-HS512`,
`A128GCM`, `A192GCM`, `A256GCM`
"""

AUTH_USER_MODEL_TABLENAME: Optional[str] = None
"""Indicates the table name for the auth user model.

`None` value means using the auto generated name by Turbulette.

Default: `None`
"""
