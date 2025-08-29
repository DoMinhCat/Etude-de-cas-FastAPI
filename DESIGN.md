## Logical Schema

The database is based on **5 main tables**:

- **Organizations**: Group together customers, technicians, interventions, and events.
- **Customers**: Associated with an organization and linked to their interventions.
- **Technicians**: Employees of an organization, who can create or perform interventions.
- **Interventions**: Performed by a technician for a customer.
- **Events**: Steps or follow-ups related to an intervention.

## Key Modeling Choices

- Addition of a **created_by** field in the _Event_ table to track the author (technician).
- Clear hierarchical relationships: An organization is the root entity, and all other tables are linked to it.
- Explicit dependency management with deletion rules tailored to business needs.

## Transition Rules (on delete)

- **CASCADE**:
- Organization → Technicians, Clients, Interventions, Events
- Client → Interventions
- Intervention → Events

> Allows automatic deletion of dependent entities.

- **RESTRICT**:
- Technician → Interventions

> Prevents a technician from being deleted as long as interventions are associated with them.

- **SET NULL**:
- Event.created_by → Technician
> An event can persist even if its creator is deleted.

## Tradeoffs

- **Simplicity vs. Integrity**: The _CASCADE_ strategy facilitates overall management in the event of an organization deletion, but results in the loss of all related data.
- **Traceability**: The _created_by_ field improves action tracking, at the cost of an optional relationship (_SET NULL_). - **Business consistency**: The use of _RESTRICT_ for technicians ensures that no intervention remains without an active manager.

This design allows for **flexibility**, **traceability**, and **business consistency**, while ensuring effective maintenance thanks to ORM and migration management (Alembic).
