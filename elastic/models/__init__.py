from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy import DECIMAL, NVARCHAR
from sqlalchemy.orm import relationship
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

class Twits(db.Model):
    __tablename__ = "twits"
    twit_id = Column(INTEGER, primary_key=True)
    user_name = Column(NVARCHAR(100))
    uploaded_on = Column(DateTime, default=datetime.now())
    twits= Column(NVARCHAR(5000))

class RegionMaster(db.Model):
    __tablename__ = "region_master"

    region_id = Column(INTEGER, primary_key=True)
    kearney_reporting_region = Column(NVARCHAR(150))
    load_date = Column(DateTime, default=datetime.utcnow)
    PrimaryKeyConstraint(
        name=build_constraints(
            is_pk=True, table1_name="region_master", column_name="region_id"
        ),
    )

    @classmethod
    def get_id_by_name(cls, region):
        return (
            cls.query.filter(cls.kearney_reporting_region == region).first().region_id
        )

class IndustryGroupMaster(db.Model):
    __tablename__ = "industry_group_master"

    industry_grp_id = Column(INTEGER, primary_key=True)
    industry = Column(NVARCHAR(100))
    industry_group = Column(NVARCHAR(100))
    load_date = Column(DateTime, default=datetime.utcnow)
    PrimaryKeyConstraint(
        name=build_constraints(
            is_pk=True,
            table1_name="industry_group_master",
            column_name="industry_grp_id",
        ),
    )


class Country(db.Model):
    __tablename__ = "country"

    country_id = Column(INTEGER, primary_key=True)
    country_code_alpha2 = Column(NVARCHAR(2))
    country_code_alpha3 = Column(NVARCHAR(3))
    country = Column(NVARCHAR(150))
    region_id = Column(
        ForeignKey(
            RegionMaster.region_id,
            name=build_constraints(
                is_fk=True,
                table1_name="country",
                table2_name="region_master",
                column_name="region_id",
            ),
        )
    )
    load_date = Column(DateTime, default=datetime.utcnow)
    PrimaryKeyConstraint(
        name=build_constraints(
            is_pk=True, table1_name="country", column_name="country_id"
        ),
    )
    region = relationship("RegionMaster", backref="region", lazy=True)

    @classmethod
    def get_id_by_name(cls, country_name):
        return cls.query.filter(cls.country == country_name).first().country_id


class CategoryLevel(db.Model):
    __tablename__ = "category_level"
    category_level_id = Column(INTEGER, primary_key=True)
    category_level_name = Column(NVARCHAR(100))
    PrimaryKeyConstraint(
        name=build_constraints(
            is_pk=True, table1_name="category_level", column_name="category_level_id"
        ),
    )


class CategoryTree(db.Model):
    __tablename__ = "category_tree"

    category_id = Column(INTEGER, primary_key=True)
    category_level_id = Column(
        ForeignKey(
            CategoryLevel.category_level_id,
            name=build_constraints(
                is_fk=True,
                table1_name="category_tree",
                table2_name="category_level",
                column_name="category_level_id",
            ),
        )
    )
    category_name = Column(NVARCHAR(100))
    category_desc = Column(NVARCHAR(255))
    parent_id = Column(
        ForeignKey(
            "category_tree.category_id",
            name=build_constraints(
                is_fk=True,
                table1_name="category_tree",
                table2_name="category_level",
                column_name="parent_id",
            ),
        )
    )
    is_active = Column(TINYINT)
    created_date = Column(DateTime, default=datetime.utcnow)
    PrimaryKeyConstraint(
        name=build_constraints(
            is_pk=True, table1_name="category_tree", column_name="category_id"
        ),
    )

    @classmethod
    def get_id_by_name(cls, category_name):
        return cls.query.filter(cls.category_name == category_name).first().category_id

    @classmethod
    def get_id_by_name_parent_id(cls, category_name, parent_id):
        return (
            cls.query.filter(
                cls.category_name == category_name, cls.parent_id == parent_id
            )
            .first()
            .category_id
        )

    @classmethod
    def get_id_by_name_for_file_validation(cls, category_name):
        data = cls.query.filter(cls.category_name == category_name).first()
        if data is not None:
            return data.category_id

    @classmethod
    def get_id_by_name_parent_id_for_file_validation(cls, category_name, parent_id):
        data = cls.query.filter(
            cls.category_name == category_name, cls.parent_id == parent_id
        ).first()
        if data is not None:
            return data.category_id



class SupplierMaster(db.Model):
    __tablename__ = "supplier_master"

    supplier_id = Column(INTEGER, primary_key=True)
    supplier_name = Column(NVARCHAR(500))
    rating = Column(NVARCHAR(10))
    is_active = Column(TINYINT)
    created_date = Column(DateTime, default=datetime.utcnow)
    modified_date = Column(DateTime, onupdate=datetime.utcnow)
    job_id = Column(NVARCHAR(255))

    PrimaryKeyConstraint(
        name=build_constraints(
            is_pk=True, table1_name="supplier_master", column_name="supplier_id"
        )
    )

    @staticmethod
    def update_supplier(
        supplier_id: int, supplier_name: str = None, is_active=None, job_id: str = None
    ):
        supplier = SupplierMaster.query.filter_by(supplier_id=supplier_id).first()

        if supplier_name is not None:
            supplier.supplier_name = supplier_name

        if is_active is not None:
            supplier.is_active = is_active

        if job_id is not None:
            supplier.job_id = job_id

        # pylint: disable=no-member
        db.session.add(supplier)
        db.session.commit()
        return supplier

    @staticmethod
    def create_supplier(
        supplier_name,
        job_id,
        is_active=1,
    ):
        supplier = SupplierMaster.query.filter_by(supplier_name=supplier_name).first()

        if supplier is not None:
            if not supplier.is_active:
                supplier.is_active = True
                db.session.add(supplier)
                SupplierMaster.update_supplier(
                    supplier_id=supplier.supplier_id,
                    supplier_name=supplier_name,
                    is_active=is_active,
                    job_id=job_id,
                )
                return supplier

        supplier = SupplierMaster()
        supplier.supplier_name = supplier_name
        supplier.is_active = is_active
        supplier.job_id = job_id
        db.session.add(supplier)
        db.session.commit()
        return supplier


class SupplierAdditionalAttribute(db.Model):
    __tablename__ = "supplier_additional_attribute"
    supplier_attribute_id = Column(INTEGER, primary_key=True)
    supplier_id = Column(
        ForeignKey(
            SupplierMaster.supplier_id,
            name=build_constraints(
                is_fk=True,
                table1_name="supplier_additional_attribute",
                table2_name="supplier_master",
                column_name="supplier_id",
            ),
        ),
        nullable=False,
    )
    attribute_type = Column(NVARCHAR(100))
    attribute_type_subgrouping = Column(NVARCHAR(50))
    attribute_name = Column(NVARCHAR(20))
    attribute_value = Column(NVARCHAR(200))
    uploaded_by = Column(
        ForeignKey(
            User.user_id,
            name=build_constraints(
                is_fk=True,
                table1_name="supplier_additional_attribute",
                table2_name="users",
                column_name="user_id",
            ),
        ),
        nullable=True,
    )

    is_active = Column(TINYINT)
    uploaded_on = Column(DateTime, default=datetime.utcnow)

    PrimaryKeyConstraint(
        name=build_constraints(
            is_pk=True,
            table1_name="supplier_additional_attribute",
            column_name="supplier_attribute_id",
        )
    )
    supplier = relationship(
        "SupplierMaster", backref="supplier_additional_attribute", lazy=True
    )


class SupplierContact(db.Model):
    __tablename__ = "supplier_contact"
    supplier_contact_id = Column(INTEGER, primary_key=True)
    supplier_id = Column(
        ForeignKey(
            SupplierMaster.supplier_id,
            name=build_constraints(
                is_fk=True,
                table1_name="supplier_contact",
                table2_name="supplier_master",
                column_name="supplier_id",
            ),
        ),
        nullable=False,
    )

    contact_name = Column(NVARCHAR(100))
    email_address = Column(NVARCHAR(50))
    contact_number = Column(NVARCHAR(20))
    designation = Column(NVARCHAR(25))
    is_active = Column(TINYINT)
    uploaded_by = Column(
        ForeignKey(
            User.user_id,
            name=build_constraints(
                is_fk=True,
                table1_name="supplier_contact",
                table2_name="users",
                column_name="user_id",
            ),
        ),
        nullable=True,
    )
    uploaded_on = Column(DateTime, default=datetime.utcnow)

    PrimaryKeyConstraint(
        name=build_constraints(
            is_pk=True,
            table1_name="supplier_contact",
            column_name="supplier_contact_id",
        )
    )

    supplier = relationship("SupplierMaster", backref="supplier_contact", lazy=True)


class SupplierCategory(db.Model):
    __tablename__ = "supplier_category"

    supplier_category_id = Column(INTEGER, primary_key=True)
    supplier_id = Column(
        ForeignKey(
            SupplierMaster.supplier_id,
            name=build_constraints(
                is_fk=True,
                table1_name="supplier_category",
                table2_name="supplier_master",
                column_name="supplier_id",
            ),
        ),
        nullable=False,
    )
    client = Column(NVARCHAR(200))
    leaf_category_id = Column(
        ForeignKey(
            CategoryTree.category_id,
            name=build_constraints(
                is_fk=True,
                table1_name="supplier_category",
                table2_name="category_tree",
                column_name="leaf_category_id",
            ),
        )
    )
    spend_year = Column(INTEGER)
    spend_usd = Column(DECIMAL(20, 4))
    region_id = Column(
        ForeignKey(
            RegionMaster.region_id,
            name=build_constraints(
                is_fk=True,
                table1_name="supplier_category",
                table2_name="region_master",
                column_name="region_id",
            ),
        )
    )
    country_id = Column(
        ForeignKey(
            Country.country_id,
            name=build_constraints(
                is_fk=True,
                table1_name="supplier_category",
                table2_name="country",
                column_name="country_id",
            ),
        )
    )
    industry_grp_id = Column(
        ForeignKey(
            IndustryGroupMaster.industry_grp_id,
            name=build_constraints(
                is_fk=True,
                table1_name="supplier_category",
                table2_name="industry_group_master",
                column_name="industry_grp_id",
            ),
        )
    )
    uploaded_by = Column(
        ForeignKey(
            User.user_id,
            name=build_constraints(
                is_fk=True,
                table1_name="supplier_category",
                table2_name="users",
                column_name="user_id",
            ),
        ),
        nullable=False,
    )
    is_active = Column(TINYINT)
    uploaded_on = Column(DateTime, onupdate=datetime.utcnow)

    PrimaryKeyConstraint(
        name=build_constraints(
            is_pk=True,
            table1_name="supplier_category",
            column_name="supplier_category_id",
        ),
    )

    Country = relationship("Country", backref="supplier_category", lazy=True)
    Industry_Group_Master = relationship(
        "IndustryGroupMaster", backref="supplier_category", lazy=True
    )
    Leaf_Category = relationship("CategoryTree", backref="supplier_category", lazy=True)
    Region = relationship("RegionMaster", backref="supplier_category", lazy=True)
    Supplier = relationship("SupplierMaster", backref="supplier_category", lazy=True)

class SupplierMetadata(db.Model):
    __tablename__ = "supplier_metadata"

    supplier_metadata_id = Column(INTEGER, primary_key=True)
    supplier_id = Column(
        ForeignKey(
            SupplierMaster.supplier_id,
            name=build_constraints(
                is_fk=True,
                table1_name="supplier_metadata",
                table2_name="supplier_master",
                column_name="supplier_id",
            ),
        ),
        nullable=False,
    )
    revenue_year = Column(INTEGER)
    revenue_usd = Column(DECIMAL(20, 4))
    credit_score = Column(INTEGER)
    diversity_score = Column(INTEGER)
    supplier_address = Column(NVARCHAR(200))
    uploaded_by = Column(
        ForeignKey(
            User.user_id,
            name=build_constraints(
                is_fk=True,
                table1_name="supplier_metadata",
                table2_name="users",
                column_name="user_id",
            ),
        ),
        nullable=True,
    )
    uploaded_on = Column(DateTime, onupdate=datetime.utcnow)
    PrimaryKeyConstraint(
        name=build_constraints(
            is_pk=True,
            table1_name="supplier_metadata",
            column_name="supplier_metadata_id",
        ),
    )

    Supplier = relationship("SupplierMaster", backref="supplier_metadata", lazy=True)

