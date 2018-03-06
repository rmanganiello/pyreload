HOOK_MANAGER_SINGLETON = 'hook_manager_singleton'
REQUEST_FACTORY_SINGLETON = 'request_factory_singleton'

ALLOWED_SINGLETONS = frozenset({
    HOOK_MANAGER_SINGLETON,
    REQUEST_FACTORY_SINGLETON,
})


class SingletonFactory(object):
    instances = {}

    @classmethod
    def get_instance(cls, name):
        instance = cls.instances.get(name)

        if instance is None:
            raise ValueError('Factory "{}" has not been instantiated'.format(name))
        return instance

    @classmethod
    def set_instance(cls, name, instance):
        if name not in ALLOWED_SINGLETONS:
            raise ValueError('Unsupported singleton "{}"'.format(name))
        cls.instances[name] = instance


def get_request_factory():
    return SingletonFactory.get_instance(REQUEST_FACTORY_SINGLETON)


def set_request_factory(instance):
    SingletonFactory.set_instance(REQUEST_FACTORY_SINGLETON, instance=instance)


def get_hook_manager():
    return SingletonFactory.get_instance(HOOK_MANAGER_SINGLETON)


def set_hook_manager(instance):
    SingletonFactory.set_instance(HOOK_MANAGER_SINGLETON, instance=instance)
