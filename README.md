# Pathways to Purpose Opportunities MVP

This is a Streamlit proof-of-concept for a Mercer-owned, globally indexed independent opportunities database. It now includes both sides of the proof-of-concept loop:

1. Faculty/staff submit an opportunity lead through a lightweight in-app form.
2. Admins review the submission queue and convert a lead into a hidden draft opportunity record.
3. Students/advisors search or match against approved/prototype opportunity records.

## MVP assumptions

- `Branded QEP 2.10.26 FJ.pdf` is the authoritative source.
- Dominican Republic is the first build node.
- Greece is the second build node.
- Macon/US local-global pathways are modeled as a future-facing "global starts local" node.
- Submitters are Mercer faculty/staff/admins only for this phase.
- Records are hidden until admin approval.
- GIC Directors/regional leads conduct initial validation.
- QEP Co-Directors/admin approve publication.
- Student saved/interested records are not persistent in P0; add after search/filter is proven.
- Do not store real sensitive student data or real documents in this prototype.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Main tabs

- **Submitter form**: DR, Greece, Macon/US local-global, and future-node forms for faculty/staff opportunity leads.
- **Submission queue**: admin-facing review queue; includes status updates and a button to convert a submission into a hidden draft record.
- **Search**: student/advisor opportunity browsing.
- **Student profile match**: soft-fit demonstration using sample profiles.
- **Advisor demo**: advising matrix showing fit guidance and readiness gaps.
- **Admin review**: opportunity-level workflow model.
- **Data notes**: governance and P0/P1 boundaries.

## Data files

- `data/opportunities.csv`
- `data/requirements.csv`
- `data/pathways.csv`
- `data/global_nodes.csv`
- `data/evidence_types.csv`
- `data/admin_workflow.csv`
- `data/student_profiles.csv`
- `data/submissions.csv`
- `data/submission_uploads/`

## Intake loop demo

1. Open the **Submitter form** tab.
2. Pick **Dominican Republic** or **Greece**.
3. Enter a test opportunity lead.
4. Submit the form.
5. Open **Submission queue**.
6. Review the submitted record.
7. Click **Convert to hidden draft opportunity**.
8. Open **Admin review** or **Search** with "All prototype records" to see the created record.

## Online deployment note

The included version writes form submissions to local CSV files inside the Streamlit app folder. This is acceptable for local demos and controlled proof-of-concept work. For a public or long-running online deployment, connect the form to durable storage such as Microsoft Lists/SharePoint, Azure SQL, Dataverse, or another approved storage service.

## Focus group script

1. Ask older faculty/staff to submit a DR or Greece lead using the form.
2. Ask whether any questions are confusing, too technical, or too long.
3. Ask admins whether the submitted record gives enough information to validate the lead.
4. Ask students to search by Dominican Republic, Greece, and Macon/US local-global.
5. Ask students whether opportunity cards explain what the opportunity is and how it connects to a global pathway.
6. Ask students whether the soft labels ("Strong fit", "Possible fit", "Build readiness", "Explore with advisor") are understandable.
7. Ask advisors whether the missing-readiness language helps them guide a student.
