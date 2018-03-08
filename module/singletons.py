ACCOUNT_MANAGER_SINGLETON = 'account_manager_singleton'
CAPTCHA_MANAGER_SINGLETON = 'captcha_manager_singleton'
HOOK_MANAGER_SINGLETON = 'hook_manager_singleton'
PULL_MANAGER_SINGLETON = 'pull_manager_singleton'
REMOTE_MANAGER_SINGLETON = 'remote_manager_singleton'
REQUEST_FACTORY_SINGLETON = 'request_factory_singleton'
THREAD_MANAGER_SINGLETON = 'thread_manager_singleton'

ALLOWED_SINGLETONS = frozenset({
    ACCOUNT_MANAGER_SINGLETON,
    CAPTCHA_MANAGER_SINGLETON,
    HOOK_MANAGER_SINGLETON,
    PULL_MANAGER_SINGLETON,
    REMOTE_MANAGER_SINGLETON,
    REQUEST_FACTORY_SINGLETON,
    THREAD_MANAGER_SINGLETON,
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


def get_account_manager():
    return SingletonFactory.get_instance(ACCOUNT_MANAGER_SINGLETON)


def set_account_manager(instance):
    SingletonFactory.set_instance(ACCOUNT_MANAGER_SINGLETON, instance=instance)


def get_captcha_manager():
    return SingletonFactory.get_instance(CAPTCHA_MANAGER_SINGLETON)


def set_captcha_manager(instance):
    SingletonFactory.set_instance(CAPTCHA_MANAGER_SINGLETON, instance=instance)


def get_hook_manager():
    return SingletonFactory.get_instance(HOOK_MANAGER_SINGLETON)


def set_hook_manager(instance):
    SingletonFactory.set_instance(HOOK_MANAGER_SINGLETON, instance=instance)


def get_pull_manager():
    return SingletonFactory.get_instance(PULL_MANAGER_SINGLETON)


def set_pull_manager(instance):
    SingletonFactory.set_instance(PULL_MANAGER_SINGLETON, instance=instance)


def get_remote_manager():
    return SingletonFactory.get_instance(REMOTE_MANAGER_SINGLETON)


def set_remote_manager(instance):
    SingletonFactory.set_instance(REMOTE_MANAGER_SINGLETON, instance=instance)


def get_request_factory():
    return SingletonFactory.get_instance(REQUEST_FACTORY_SINGLETON)


def set_request_factory(instance):
    SingletonFactory.set_instance(REQUEST_FACTORY_SINGLETON, instance=instance)


def get_thread_manager():
    return SingletonFactory.get_instance(THREAD_MANAGER_SINGLETON)


def set_thread_manager(instance):
    SingletonFactory.set_instance(THREAD_MANAGER_SINGLETON, instance=instance)
