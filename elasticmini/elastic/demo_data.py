from flask.cli import AppGroup, with_appcontext
from elastic.extensions import db
from elastic.models import User, Role, Client, UserClientMap, Action
import logging
from faker import Faker

roles = [
    User.ROLE_SME,
    User.ROLE_KEARNEY_USER,
    User.ROLE_ADMIN,
    User.ROLE_POWER_USER
]


actions = [
    Action.REJECT,
    Action.ACTION_RAW_FILE_UPLOADED,
    Action.NORMALIZED_UPLOADED,
    Action.APPROVED,
    Action.REQUESTED,
    Action.EXPORT
]

data_cli = AppGroup("data", help="elasticmarking custom CLI commands")


@data_cli.command(name="test")
@with_appcontext
def deploy():
    print("Test")


@data_cli.command(name="upload")
@with_appcontext
def upload():
    """deploy command used create all necessary tables\
         and insert necessary entries while starting the application.
    """
    # Drop all the tables from existing Database.
    # db.drop_all()

    # Create Database
    db.create_all()
    #
    # create_user_roles(roles)
    # create_actions(actions)
    # create_test_users()
    create_test_clients()
    # create_user_client_map()


def create_user_roles(seed_roles):
    """Method used to create initial/dummy user's roles for the application."""
    for _role in seed_roles:
        if not Role.lookup(str(_role)):
            Role.create_role(
                role_name=str(_role),
                role_desc=_role,
                is_active=True,
            )
    logging.info("Users roles creation finished")


def create_actions(seed_actions):
    for _action in seed_actions:
        if not Action.lookup(str(_action)):
            Action.create_action(
                action_name=str(_action),
                is_active=True,
            )
    logging.info("Actions creation finished")


def create_test_users():
    print("Create users")
    for _ in range(10):
        fake = Faker("en_Us")
        User.create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
        )


def create_test_clients():
    print("Create clients")
    Faker.seed()
    fake = Faker("en_US")
    for _ in range(10):
        name = fake.company()
        Client.create_client(client_name=name, is_active=True)


def create_user_client_map():
    for i in range(4):
        m = UserClientMap()
        m.user_id = 11
        m.client_id = i+1
        m.is_active = True
        db.session.add(m)
        db.session.commit()
