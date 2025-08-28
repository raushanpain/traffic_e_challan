class ChallanRouter:
    """
    A router to control all database operations on models for the
    challan application.
    """
    def db_for_read(self, model, **hints):
        """
        Suggest the database to use for reads of objects of type model.
        """
        if model._meta.app_label == 'challan_app':
            return 'challan_db'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Suggest the database to use for writes of objects of type model.
        """
        if model._meta.app_label == 'challan_app':
            return 'challan_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow any relation if a model in challan_app is involved.
        """
        if obj1._meta.app_label == 'challan_app' or \
           obj2._meta.app_label == 'challan_app':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the challan_app app gets created on the right database.
        """
        if app_label == 'challan_app':
            return db == 'challan_db'
        return None
