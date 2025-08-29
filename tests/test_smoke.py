import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas.intervention import InterventionStatus, CreateItem, PatchItem
from app.schemas.client import CreateClient
from app.models.event import Event
from app.models.client import Client
from app.models.technician import Technician
from app.models.intervention import Intervention
from app.models.organisation import Organisation
from app.db.base import Base
from app.api.routers.clients import create_client, get_client
from app.api.routers.interventions import create_item, update_item
from app.api.routers.events import list_events

# Use SQLite in-memory for tests
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


# --- TESTS ---
# Creation client
def test_create_client_ok(db):
    # Create org for foreign key
    org = Organisation(name="TestOrg", street="1 Main St", postal_code="12345")
    db.add(org)
    db.commit()
    db.refresh(org)
    new_client = CreateClient(
        first_name="Test",
        last_name="Client",
        username="testclient",
        password="password",
        email="testclient@example.com",
        phone="0123456789"
    )
    class DummyUser:
        org_id = org.id
    client = create_client(new_client, current_user=DummyUser(), db=db, current_role=None)
    assert "message" in client


def test_create_client_error_missing_name(db):
    # Create org for foreign key
    org = Organisation(name="TestOrg", street="1 Main St", postal_code="12345")
    db.add(org)
    db.commit()
    db.refresh(org)
    # Missing username
    with pytest.raises(ValidationError):
        CreateClient(
            first_name="Test",
            last_name="Client",
            username=None,
            password="password",
            email="testclient@example.com",
            phone="0123456789"
        )


# Creation item liée au client
def test_create_item_same_org(db):
    # Create org, client and technician
    org = Organisation(name="OrgA", street="2 Main St", postal_code="23456")
    db.add(org)
    db.commit()
    db.refresh(org)
    class DummyUser:
        org_id = org.id
    client = CreateClient(
        first_name="A",
        last_name="A",
        username="clienta",
        password="pw",
        email="a@a.com",
        phone="111"
    )
    create_client(client, current_user=DummyUser(), db=db, current_role=None)
    db.commit()
    client_id = db.query(Client).filter_by(org_id=org.id).first().id
    tech = Technician(username="tech1", org_id=org.id, hashed_password="pw", email="tech1@a.com", name="Tech One")
    db.add(tech)
    db.commit()
    tech_id = tech.id
    item = CreateItem(client_id=client_id, technician_id=tech_id, description="desc", status=InterventionStatus.PENDING)
    result = create_item(item, current_user=DummyUser(), db=db, current_role=None)
    assert "message" in result


def test_create_item_different_org_fail(db):
    org1 = Organisation(name="OrgA", street="2 Main St", postal_code="23456")
    org2 = Organisation(name="OrgB", street="3 Main St", postal_code="34567")
    db.add_all([org1, org2])
    db.commit()
    db.refresh(org1)
    db.refresh(org2)
    class DummyUser:
        org_id = org1.id
    client = CreateClient(
        first_name="A",
        last_name="A",
        username="clientb",
        password="pw",
        email="b@b.com",
        phone="222"
    )
    create_client(client, current_user=DummyUser(), db=db, current_role=None)
    db.commit()
    client_id = db.query(Client).filter_by(org_id=org1.id).first().id
    tech = Technician(username="tech2", org_id=org2.id, hashed_password="pw", email="tech2@b.com", name="Tech Two")
    db.add(tech)
    db.commit()
    tech_id = tech.id
    item = CreateItem(client_id=client_id, technician_id=tech_id, description="desc", status=InterventionStatus.PENDING)
    class DummyUser2:
        org_id = org2.id
    with pytest.raises(HTTPException):
        create_item(item, current_user=DummyUser2(), db=db, current_role=None)


# Status transition
def test_status_transition_valid(db):
    org = Organisation(name="OrgC", street="4 Main St", postal_code="45678")
    db.add(org)
    db.commit()
    db.refresh(org)
    class DummyUser:
        org_id = org.id
    client = CreateClient(
        first_name="A",
        last_name="A",
        username="clientc",
        password="pw",
        email="c@c.com",
        phone="333"
    )
    create_client(client, current_user=DummyUser(), db=db, current_role=None)
    db.commit()
    client_id = db.query(Client).filter_by(org_id=org.id).first().id
    tech = Technician(username="tech3", org_id=org.id, hashed_password="pw", email="tech3@c.com", name="Tech Three")
    db.add(tech)
    db.commit()
    tech_id = tech.id
    item = CreateItem(client_id=client_id, technician_id=tech_id, description="desc", status=InterventionStatus.PENDING)
    create_item(item, current_user=DummyUser(), db=db, current_role=None)
    db.commit()
    intervention = db.query(Intervention).filter_by(org_id=org.id).first()
    patch = PatchItem(status=InterventionStatus.IN_PROGRESS)
    update_item(intervention.id, patch, db=db, current_user=DummyUser(), current_role=None)
    updated = db.query(Intervention).filter_by(id=intervention.id).first()
    assert updated.status == InterventionStatus.IN_PROGRESS


def test_status_transition_invalid(db):
    org = Organisation(name="OrgD", street="5 Main St", postal_code="56789")
    db.add(org)
    db.commit()
    db.refresh(org)
    class DummyUser:
        org_id = org.id
    client = CreateClient(
        first_name="A",
        last_name="A",
        username="clientd",
        password="pw",
        email="d@d.com",
        phone="444"
    )
    create_client(client, current_user=DummyUser(), db=db, current_role=None)
    db.commit()
    client_id = db.query(Client).filter_by(org_id=org.id).first().id
    tech = Technician(username="tech4", org_id=org.id, hashed_password="pw", email="tech4@d.com", name="Tech Four")
    db.add(tech)
    db.commit()
    tech_id = tech.id
    item = CreateItem(client_id=client_id, technician_id=tech_id, description="desc", status=InterventionStatus.PENDING)
    create_item(item, current_user=DummyUser(), db=db, current_role=None)
    db.commit()
    intervention = db.query(Intervention).filter_by(org_id=org.id).first()
    with pytest.raises(ValidationError):
        PatchItem(status="INVALID_STATUS")


# Filter by org
def test_filter_clients_by_org(db):
    org1 = Organisation(name="OrgE", street="6 Main St", postal_code="67890")
    org2 = Organisation(name="OrgF", street="7 Main St", postal_code="78901")
    db.add_all([org1, org2])
    db.commit()
    db.refresh(org1)
    db.refresh(org2)
    class DummyUser1:
        org_id = org1.id
    class DummyUser2:
        org_id = org2.id
    client1 = CreateClient(
        first_name="A",
        last_name="A",
        username="orga1",
        password="pw",
        email="orga1@a.com",
        phone="555"
    )
    client2 = CreateClient(
        first_name="B",
        last_name="B",
        username="orga2",
        password="pw",
        email="orga2@b.com",
        phone="666"
    )
    create_client(client1, current_user=DummyUser1(), db=db, current_role=None)
    create_client(client2, current_user=DummyUser2(), db=db, current_role=None)
    db.commit()
    client1_id = db.query(Client).filter_by(org_id=org1.id).first().id
    client2_id = db.query(Client).filter_by(org_id=org2.id).first().id
    c1 = get_client(client1_id, current_user=DummyUser1(), db=db, current_role=None)
    c2 = get_client(client2_id, current_user=DummyUser2(), db=db, current_role=None)
    assert hasattr(c1, "organisation") and c1.organisation == org1.name
    assert hasattr(c2, "organisation") and c2.organisation == org2.name


# Timeline
def test_timeline_creation_and_order(db):
    org = Organisation(name="Org1", street="8 Main St", postal_code="89012")
    db.add(org)
    db.commit()
    db.refresh(org)
    client = Client(
        first_name="Timeline",
        last_name="Client",
        username="timelineclient",
        hashed_password="pw",
        email="timeline@client.com",
        phone="999",
        org_id=org.id
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    tech = Technician(username="tech5", org_id=org.id, hashed_password="pw", email="tech5@e.com", name="Tech Five")
    db.add(tech)
    db.commit()
    db.refresh(tech)
    intervention = Intervention(client_id=client.id, org_id=org.id, technician_id=tech.id, description="desc", status=InterventionStatus.PENDING)
    db.add(intervention)
    db.commit()
    db.refresh(intervention)
    e1 = Event(intervention_id=intervention.id, organisation_id=org.id, technician_id=tech.id, type="started", note="created")
    e2 = Event(intervention_id=intervention.id, organisation_id=org.id, technician_id=tech.id, type="updated", note="updated")
    db.add_all([e1, e2])
    db.commit()
    class DummyUser:
        org_id = org.id
    timeline = list_events(intervention.id, current_user=DummyUser(), db=db)
    assert [e.note for e in timeline] == ["created", "updated"]
    assert [e.note for e in timeline] == ["created", "updated"]
