from ariadne.types import GraphQLResolveInfo


def is_query(info: GraphQLResolveInfo) -> bool:
    root_names = []
    for type_ in [
        info.schema.query_type,
        info.schema.mutation_type,
        info.schema.subscription_type,
    ]:
        if type_:
            root_names.append(type_.name)
    return info.parent_type.name in root_names
