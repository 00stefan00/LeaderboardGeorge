import jsonstorage
from constants import Constants


REQUIRED_VERSION = 1 

class MigrationHelper:

    def __init__(self, server_id):
        self.server_id = server_id
        if not self.has_migration_version():
            self.set_migration_version(0)
        self.current_version = self.get_migration_version()

    def check_for_updates(self):
        while self.current_version < REQUIRED_VERSION:
            print "update from {} to {}".format(self.current_version, REQUIRED_VERSION)
            self.current_version += 1
            if self.current_version == 1:
                self.update_one()
            if self.current_version == 2:
                #self.update_two()
                pass

    def has_migration_version(self):
        try:
            version = jsonstorage.get(self.server_id, Constants.migration_version.fget())
            return True
        except Exception:
            return False

    def has_storage_field(self, key):
        try:
            value = jsonstorage.get(self.server_id, key)
            return True
        except Exception:
            return False

    def get_migration_version(self):
        return jsonstorage.get(self.server_id, Constants.migration_version.fget())

    def set_migration_version(self, version):
        jsonstorage.add(self.server_id, Constants.migration_version.fget(), version)

    def update_one(self):
        try:
            pass
        except:
            # Todo, notify discord server of failed migration and advice reconfiguration
            pass
