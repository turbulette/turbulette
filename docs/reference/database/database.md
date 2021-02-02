Turbulette doesn't add much on top of GINO, what is does is basically set up the `Gino` instance
at startup and extend the base `Model` class to automatically generate `__tablename__` attribute.
The rest is pure [GINO](https://python-gino.org/docs/en/master/index.html).

## `Model`

Base model for GINO models.

It's close to the base GINO Model class, the main difference is
that `__tablename__` class attribute (the table name) is automatically generated based
on the Turbulette app name and the model name, in camel case format.

If the following model leaves in a Turbulette app named `vehicle` :

!!! example
    ```python
    from turbulette.db import Model

    class SuperCar(Model):
        pass
    ```

Then the resulting generated `__tablename__` attribute will be `vehicle_super_car`


::: turbulette.db.database
    selection:
        filters:
            - "!^(Model|BaseModelMeta)$$"
