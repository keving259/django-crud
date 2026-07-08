from django.conf import settings
import sys

class MasterSlaveRouter:
    def db_for_read(self, model, **hints):
        if 'test' in sys.argv:
            return 'default'
        
        if settings.DEBUG:
            return 'default'
        return 'replica'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == 'default'