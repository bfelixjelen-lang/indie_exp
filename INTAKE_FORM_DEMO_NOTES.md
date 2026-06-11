# Intake Form Demo Notes

## Purpose

This file documents the in-app submitter form added to the Streamlit MVP. The form is meant to show how the opportunity database can be populated before Microsoft Forms, Power Automate, or enterprise storage are introduced.

## Why model the form in Streamlit?

The first reviewers are likely to care less about backend architecture and more about whether faculty/staff understand the questions. A Streamlit form lets the team test language, ordering, dropdowns, and admin review before building the final Microsoft intake process.

## Submitter design principles

- Use familiar, plain-language labels.
- Let submitters write "unknown" instead of blocking submission.
- Keep DR, Greece, Macon/US local-global, and Other/Future in separate tabs.
- Ask for enough detail to support matching, but avoid making the form feel like a grant application.
- Treat the submitted record as a lead, not as an approved opportunity.

## Intake-to-database workflow

1. Submitter completes a tabbed in-app form.
2. The app writes a row to `data/submissions.csv`.
3. Optional backup files are stored under `data/submission_uploads/<submission_id>/`.
4. Admin reviews the queue.
5. Admin changes the review status or converts the lead into a hidden draft opportunity record.
6. Conversion writes records to:
   - `data/opportunities.csv`
   - `data/requirements.csv`
   - `data/pathways.csv`
7. Converted records remain hidden until publication approval.

## Production caveat

Local CSV writing is not a production storage model for a deployed web app. It is a prototype device. The likely enterprise path is Microsoft Lists/SharePoint or Dataverse for intake/review, then a front-end app that reads approved records.

## Suggested focus-group questions for submitters

- Could you complete this without training?
- Which question would make you stop and ask for help?
- Are the DR/Greece tabs intuitive?
- Do you understand the difference between an opportunity lead and an approved student-facing opportunity?
- Would you rather fill out the short version first and have an admin follow up, or complete more details on the first pass?
- Are there fields missing that you would expect to provide?
