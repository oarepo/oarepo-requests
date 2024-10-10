def user_mappings(identity):
    return [{"user": identity.id}]


def group_mappings(identity):
    roles = [n.value for n in identity.provides if n.method == "role"]
    return [{"group": role_id} for role_id in roles]
