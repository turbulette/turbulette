## Isn't the project structure similar to Django's one?

If you already used Django before, you probably noticed similarities with the project structure, as Turbulette is strongly inspired by the modular design of Django apps and the default project skeleton.

The idea is to give the developers a default way of doing things while keeping the flexibility to write more complex projects.
For instance, if your resolvers have to be available under the `📁 resolvers` folder, It's just a Python package at the end.
You are free to move them elsewhere and to import them all inside `📁 resolvers`.
