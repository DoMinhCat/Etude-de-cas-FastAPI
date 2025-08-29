from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models.client import Client
from app.models.technician import Technician
from app.models.organisation import Organisation

def initial_insert():
    db: Session = SessionLocal()
    try:
        if not db.query(Client).first():
            org1 = Organisation(name="Organisation 1", street="abc", postal_code="12345")
            org2 = Organisation(name="Organisation 2", street="abc", postal_code="12345")
            db.add_all([org1, org2])
            db.commit()

            client1 = Client(
                first_name="Cat",
                last_name="DO",
                email="cat@gmail.com",
                phone="+33123456789",
                created_at=datetime.now(timezone.utc),
                org_id=org1.id,
                username="cat",
                hashed_password="$2b$12$AxQfAwvBp8FFJ905xD89juUF7yoduGuHj6Gf.TH40qUDLAWfmcfvm"
            )
            client2 = Client(
                first_name="Alex",
                last_name="DUPONT",
                email="alex@gmail.com",
                phone="+33123456788",
                created_at=datetime.now(timezone.utc),
                org_id=org2.id,
                username="alex",
                hashed_password="$2b$12$AxQfAwvBp8FFJ905xD89juUF7yoduGuHj6Gf.TH40qUDLAWfmcfvm"
            )
            db.add_all([client1, client2])
            db.commit()

            tech1 = Technician(
                email="tech1@gmail.com",
                name="tech1",
                org_id=org1.id,
                created_at=datetime.now(timezone.utc),
                username="tech1",
                hashed_password="$2b$12$AxQfAwvBp8FFJ905xD89juUF7yoduGuHj6Gf.TH40qUDLAWfmcfvm"
            )
            tech2 = Technician(
                email="tech2@gmail.com",
                name="tech2",
                org_id=org2.id,
                created_at=datetime.now(timezone.utc),
                username="tech2",
                hashed_password="$2b$12$AxQfAwvBp8FFJ905xD89juUF7yoduGuHj6Gf.TH40qUDLAWfmcfvm"
            )
            db.add_all([tech1, tech2])
            db.commit()
    finally:
        db.close()

    print("Initial data inserted.")
            
if __name__=="__main__":
    initial_insert()