from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy import DECIMAL
from sqlalchemy.orm import relationship
from elastic.constants import get_action_cache_key, SPEND, PRICE, SAVINGS
from sqlalchemy.sql.schema import PrimaryKeyConstraint


from datetime import datetime

from elastic.extensions import db, cache
from elastic.utils import (
    UserAlreadyExists,
    UserDoesNotExist,
    RecordNotFound,
)

from sqlalchemy import (
    Column,
    INTEGER,
    String,
    ForeignKey,
    DateTime,
    Boolean,
    JSON,
    Table,
    MetaData,
)
from sqlalchemy.dialects.mssql import SQL_VARIANT


def build_constraints(
    table1_name: str,
    column_name: str,
    table2_name: str = None,
    is_fk: bool = False,
    is_pk: bool = False,
):
    constraint_name = ""
    if is_fk is True:
        constraint_name += "FK__"
    if is_pk is True:
        constraint_name += "PK__"
    constraint_name += table1_name + "__"
    if is_fk is True:
        constraint_name += table2_name + "__"
    constraint_name += column_name

    return constraint_name

class Role(db.Model):
    __tablename__ = "role"

    POWER_USER_ROLE = "Power User"
    ADMIN_ROLE = "Admin"
    PRIVILEGE_USER_ROLE = "Privilege"
    SME_ROLE = "SME"
    KEARNEY_USER_ROLE = "Kearney User"

    role_id = Column(INTEGER, primary_key=True)
    role_name = Column(String(100))
    role_desc = Column(String(500))
    is_active = Column(TINYINT)
    created_date = Column(DateTime, default=datetime.utcnow)
    modified_date = Column(DateTime, onupdate=datetime.utcnow)
    PrimaryKeyConstraint(
        name=build_constraints(is_pk=True, table1_name="role", column_name="role_id"),
    )

    @staticmethod
    def create_role(role_name, role_desc=None, is_active=None):
        role = Role.query.filter_by(role_name=role_name).first()
        if role:
            return
        role = Role()
        role.role_name = role_name
        if role_desc is not None:
            role.role_desc = role_desc
        if is_active is not None:
            role.is_active = is_active
        db.session.add(role)
        db.session.commit()
        return role

    @classmethod
    def lookup(cls, role_name):
        return cls.query.filter_by(role_name=role_name).first()


class User(db.Model):
    __tablename__ = "users"

    ROLE_KEARNEY_USER = "Kearney User"
    ROLE_SME = "SME"
    ROLE_ADMIN = "Admin"
    ROLE_POWER_USER = "Power User"
    ROLE_PRIVILEGE = "Privilege"

    user_id = Column(INTEGER, primary_key=True)
    role_id = Column(
        ForeignKey(
            Role.role_id,
            name=build_constraints(
                is_fk=True,
                table1_name="users",
                table2_name="role",
                column_name="role_id",
            ),
        ),
        nullable=False,
    )
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    password = Column(String(100))
    email_address = Column(String(100))
    is_active = Column(Boolean)
    created_date = Column(DateTime, default=datetime.utcnow)
    modified_date = Column(DateTime, onupdate=datetime.utcnow)
    PrimaryKeyConstraint(
        name=build_constraints(is_pk=True, table1_name="users", column_name="user_id",),
    )

    role = relationship("Role", backref="users", lazy=True)

    @property
    def identity(self):
        return self.user_id

    @classmethod
    def lookup(cls, email):
        return cls.query.filter_by(email_address=email).first()

    @classmethod
    def lookup_active(cls, email):
        return cls.query.filter_by(email_address=email, is_active=1).first()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @property
    def roles(self):
        """Returns possible role that a user is authorised to.

        Returns:
            str: role name
        """
        return {"id": self.role.role_id, "name": self.role.role_name}

    @property
    def rolenames(self):
        """Returns list of all possible roles that a user is authorised to.

        Returns:
            list: List of roles
        """
        try:
            return self.role.role_name.split(",")
        except Exception:
            return []

    @property
    def role_name(self):

        try:
            return self.role.role_name
        except Exception:
            return ""

    @property
    def username(self):
        return self.username

    @staticmethod
    def create_user(
        first_name,
        last_name,
        email,
        roles=ROLE_KEARNEY_USER,
        is_active=1,
        approved=False,
        enable_app_login=True,
        is_admin=False,
    ):
        user = User.query.filter_by(email_address=email).first()

        if user is not None and is_admin is True:
            if not user.is_active:
                user.is_active = True
                db.session.add(user)
                db.session.commit()
                User.update_user(
                    user_id=user.user_id,
                    first_name=first_name,
                    last_name=last_name,
                    is_active=is_active,
                    approved=approved,
                    roles=roles,
                )
                return user

        if user:
            raise UserAlreadyExists

        user = User()
        user.first_name = first_name
        user.last_name = last_name
        user.email_address = email
        user.is_active = is_active

        user.approved_at = datetime.utcnow() if approved else None
        if roles is not None:
            role_id = Role.lookup(role_name=roles).role_id
            user.role_id = role_id
        user.enable_app_login = enable_app_login
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_user(
        user_id: int,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        roles: set = None,
        is_active=None,
        approved=None,
        verified=False,
        verification_code: int = None,
        failed_attempt: bool = None,
        enable_app_login: bool = None,
        reset_verification_code: bool = None,
    ):
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            raise UserDoesNotExist

        if email is not None:
            existing_user = User.query.filter_by(email_address=email).first()
            if existing_user and existing_user.user_id != user_id:
                raise UserAlreadyExists
            user.email_address = email

        if first_name is not None:
            user.first_name = first_name

        if last_name is not None:
            user.last_name = last_name

        if roles is not None:
            role_id = Role.lookup(role_name=roles).role_id
            user.role_id = role_id

        if is_active is not None:
            user.is_active = is_active

        if verified is not None and verified == True:
            user.email_verified_at = datetime.utcnow()

        if approved is True:
            user.approved_at = datetime.utcnow()

        if approved is False:
            user.approved_at = None

        if failed_attempt is True:
            user.failed_attempts = (
                int(user.failed_attempts if user.failed_attempts is not None else 0) + 1
            )
        elif failed_attempt is False:
            user.failed_attempts = 0

        if enable_app_login is not None:
            user.enable_app_login = enable_app_login

        if enable_app_login is not None:
            user.enable_app_login = enable_app_login

        if verification_code is not None:
            user.verification_code = verification_code
            user.message_sent = datetime.utcnow()

        if reset_verification_code is not None:
            user.verification_code = None
            user.message_sent = None
        # pylint: disable=no-member
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_rolename(rolename):
        users = (
            db.session.query(User)
            .filter(User.is_active == True,)
            .filter(Role.role_id == User.role_id, Role.role_name == rolename)
        ).all()
        user_ids = [user.user_id for user in users]
        return user_ids

