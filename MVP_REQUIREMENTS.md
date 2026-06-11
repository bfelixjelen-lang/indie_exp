# Pathways to Purpose Global Opportunities MVP Requirements

## 1. Product definition

A Streamlit-based proof of concept for a Mercer-owned, admin-approved, globally indexed opportunity discovery and advising tool. The tool catalogs independent opportunities in research, internships, service learning, independent work, fellowships, clinical/shadowing, advanced study, and employment pathways that build from global learning experiences.

## 2. Authoritative source and scope

The master QEP document, `Branded QEP 2.10.26 FJ.pdf`, is authoritative. The SACSCOC presentation, proposals, budget/pro forma, catalog files, Global Education website text, Mercer On Mission website text, and study abroad spreadsheets are ancillary context.

The first build prioritizes Dominican Republic, then Greece, in the same interface. Macon/United States local-global opportunities are modeled as an onshore global node for "global starts local" pathways.

## 3. Primary users

- Student: primarily Macon undergraduate, with other Mercer student types not excluded.
- Advisor: helps interpret fit/readiness and next steps.
- Admin: QEP Database and Visualization Working Group, Felix Jelen admin/owner.
- Read-only reviewer: can see hidden/unapproved records but cannot publish.
- Nominator: Mercer faculty/staff/admin only in P0/P1.

## 4. P0 goals

- Search and filter independent global opportunity records.
- Pivot between Dominican Republic and Greece.
- Show how each opportunity builds from a Mercer international/global pathway.
- Display requirements and expected readiness evidence.
- Provide soft match labels using self-attested student profile data.
- Provide an advisor view showing matched signals and build-readiness gaps.
- Provide an admin workflow model and hidden/unapproved record view.

## 5. P0 non-goals

- No live Mercer authentication.
- No real sensitive student documents.
- No official student record integration.
- No live Handshake integration.
- No external partner portal.
- No production application workflow.
- No persistent saved/interested records until search/filter is validated.

## 6. Opportunity scope

In scope:
- internships
- research
- service learning
- independent work
- fellowships
- clinical/shadowing
- advanced study
- employment pathways, mostly through Handshake or later CCPD workflow
- globally located and globally indexed onshore pathways

Out of scope as opportunity records:
- Mercer On Mission courses
- Global Education study abroad courses
- general course/program matching

Those programs may be referenced as upstream preparation, readiness evidence, or pathway context.

## 7. Validation and publication workflow

Draft -> Submitted -> Initial Validation -> Needs Clarification -> Admin Reviewed -> QEP Co-Director Approval Pending -> Approved/Published -> Expired/Annual Review -> Archived.

Initial validation belongs to the relevant GIC Director/regional lead. Final approval belongs to QEP Co-Directors/admin. Records remain hidden until approved. Annual review occurs in July, with approval/renewal by August 20.

## 8. Data model

See `qep_opportunities_mvp_schema.xlsx` for full tables and field-level details.

Core tables:
- Global_Nodes
- Opportunities
- Requirements
- Pathways
- Evidence_Types
- Student_Profile_Fields
- Admin_Workflow
- Form_Questions
- Taxonomy
- Interest_Log_Future
- Streamlit_Field_Map

## 9. Matching language

The app should not display numeric match scores. It should display:
- Strong fit
- Possible fit
- Build readiness
- Explore with advisor
- Not enough information, if needed

## 10. Manual next steps

1. Review the seed opportunity records and replace synthetic examples with real DR and Greece leads.
2. Identify the DR GIC/regional validator and Greece GIC validator names to use in records.
3. Confirm the first five real DR opportunities and first five real Greece opportunities.
4. Decide which student profile fields are acceptable in live focus groups.
5. Decide whether focus group testing uses synthetic profiles, volunteer profiles, or both.
6. Test the Streamlit app locally with OGE/QEP team.
7. Revise fields before building the Microsoft Form.
