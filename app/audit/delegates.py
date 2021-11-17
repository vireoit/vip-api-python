from app.audit.services import AuditService


class AuditLogDelegate:

    @staticmethod
    def create_audit_log(filters, user_identity):
        AuditService.create_audit_log(filters, user_identity)

    @staticmethod
    def create_anonymous_audit_log(filters):
        AuditService.create_anonymous_audit_log(filters)

    @staticmethod
    def get_all_logs(filters, user_identity):
        data = AuditService.get_all_logs(filters, user_identity)
        return data
