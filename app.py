import re
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"
SUBMISSIONS_FILE = DATA_DIR / "submissions.csv"
UPLOAD_DIR = DATA_DIR / "submission_uploads"

ORANGE = "#f97316"

SUBMISSION_COLUMNS = [
    "submission_id",
    "submitted_at",
    "submitter_name",
    "submitter_email",
    "submitter_unit",
    "submitter_role",
    "global_node_id",
    "opportunity_title",
    "opportunity_type",
    "short_description",
    "country",
    "city_region",
    "global_index_type",
    "related_mercer_experiences",
    "student_stage",
    "primary_discipline",
    "target_student_level",
    "target_majors",
    "language_requirements",
    "skill_requirements",
    "experience_requirements",
    "evidence_expected",
    "compensation_funding",
    "timing",
    "deadline",
    "partner_org",
    "partner_contact_name",
    "partner_contact_email",
    "partner_relationship_status",
    "mercer_owner",
    "owner_unit",
    "backup_files",
    "review_status",
    "admin_notes",
    "converted_opportunity_id",
]

SUBMISSION_REVIEW_STATUSES = [
    "Submitted",
    "Needs Review",
    "Needs Clarification",
    "Initial Validation Complete",
    "Admin Reviewed",
    "QEP Co-Director Approval Pending",
    "Approved/Published",
    "Archived",
]

OPPORTUNITY_TYPES = [
    "Research",
    "Service Learning",
    "Internship",
    "Advanced Study",
    "Independent Work",
    "Fellowship/Scholarship",
    "Clinical/Shadowing",
    "Employment/Handshake-linked",
    "Other / Not sure",
]

GLOBAL_INDEX_TYPES = [
    "Abroad / globally located",
    "US onshore / globally indexed",
    "Remote / virtual global",
    "Handshake/employment placeholder",
    "Other / not sure",
]

STUDENT_STAGE_OPTIONS = [
    "Pre-travel awareness",
    "In-country exploration",
    "Post-return pursuit",
    "Any stage / not sure",
]

NODE_FORM_CONFIG = {
    "GIC-DR": {
        "label": "Dominican Republic form",
        "country": "Dominican Republic",
        "help": "Use this for DR opportunities, partner leads, and pathways connected to DR experiences.",
    },
    "GIC-GR": {
        "label": "Greece form",
        "country": "Greece",
        "help": "Use this for Greece opportunities, partner leads, migration/culture pathways, and related advanced work.",
    },
    "GIC-MCN": {
        "label": "Macon / US local-global form",
        "country": "United States",
        "help": "Use this for onshore opportunities with a global index or local preparation value.",
    },
    "GIC-FUTURE": {
        "label": "Other / future node form",
        "country": "",
        "help": "Use this for early leads that do not yet fit DR, Greece, or Macon local-global pathways.",
    },
}

st.set_page_config(
    page_title="Pathways to Purpose Opportunities MVP",
    page_icon=":material/public:",
    layout="wide",
)


def ensure_submission_store():
    DATA_DIR.mkdir(exist_ok=True)
    UPLOAD_DIR.mkdir(exist_ok=True)
    if not SUBMISSIONS_FILE.exists():
        pd.DataFrame(columns=SUBMISSION_COLUMNS).to_csv(SUBMISSIONS_FILE, index=False)
        return
    df = pd.read_csv(SUBMISSIONS_FILE, dtype=str).fillna("")
    changed = False
    for col in SUBMISSION_COLUMNS:
        if col not in df.columns:
            df[col] = ""
            changed = True
    if changed:
        df[SUBMISSION_COLUMNS].to_csv(SUBMISSIONS_FILE, index=False)


def read_csv_safely(path, columns=None):
    if not path.exists():
        return pd.DataFrame(columns=columns or [])
    df = pd.read_csv(path, dtype=str).fillna("")
    if columns:
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        df = df[columns]
    return df.fillna("")


@st.cache_data
def load_data():
    ensure_submission_store()
    opportunities = pd.read_csv(DATA_DIR / "opportunities.csv", dtype=str).fillna("")
    requirements = pd.read_csv(DATA_DIR / "requirements.csv", dtype=str).fillna("")
    pathways = pd.read_csv(DATA_DIR / "pathways.csv", dtype=str).fillna("")
    nodes = pd.read_csv(DATA_DIR / "global_nodes.csv", dtype=str).fillna("")
    profiles = pd.read_csv(DATA_DIR / "student_profiles.csv", dtype=str).fillna("")
    workflow = pd.read_csv(DATA_DIR / "admin_workflow.csv", dtype=str).fillna("")
    submissions = read_csv_safely(SUBMISSIONS_FILE, SUBMISSION_COLUMNS)
    return opportunities, requirements, pathways, nodes, profiles, workflow, submissions


opportunities, requirements, pathways, nodes, profiles, workflow, submissions = load_data()


def tokens(text):
    if not isinstance(text, str):
        return set()
    return {t.lower() for t in re.split(r"[^A-Za-z0-9]+", text) if len(t) > 2}


def compact(text, fallback="Not specified"):
    value = "" if text is None else str(text).strip()
    return value if value else fallback


def combined_text(row, cols):
    return " ".join(str(row.get(c, "")) for c in cols)


def safe_filename(name):
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(name or "file"))
    return cleaned[:100] or "file"


def append_csv_row(path, columns, row):
    df = read_csv_safely(path, columns)
    clean_row = {col: str(row.get(col, "")) for col in columns}
    df = pd.concat([df, pd.DataFrame([clean_row])], ignore_index=True)
    df.to_csv(path, index=False)


def save_uploaded_files(uploaded_files, submission_id):
    if not uploaded_files:
        return ""
    saved = []
    target_dir = UPLOAD_DIR / submission_id
    target_dir.mkdir(parents=True, exist_ok=True)
    for file in uploaded_files:
        filename = safe_filename(getattr(file, "name", "uploaded_file"))
        target = target_dir / filename
        target.write_bytes(file.getvalue())
        saved.append(str(target.relative_to(DATA_DIR)))
    return "; ".join(saved)


def update_submission(submission_id, updates):
    df = read_csv_safely(SUBMISSIONS_FILE, SUBMISSION_COLUMNS)
    if df.empty or submission_id not in df["submission_id"].tolist():
        return False
    mask = df["submission_id"] == submission_id
    for key, value in updates.items():
        if key in df.columns:
            df.loc[mask, key] = str(value)
    df.to_csv(SUBMISSIONS_FILE, index=False)
    return True


def next_review_date():
    # Annual review target requested for July review and August 20 approval.
    return "2026-07-15"


def annual_approval_deadline():
    return "2026-08-20"


def build_tags_from_submission(sub):
    fields = [
        sub.get("global_node_id", ""),
        sub.get("country", ""),
        sub.get("city_region", ""),
        sub.get("opportunity_type", ""),
        sub.get("primary_discipline", ""),
        sub.get("target_majors", ""),
        sub.get("language_requirements", ""),
        sub.get("skill_requirements", ""),
    ]
    raw = "; ".join([str(x) for x in fields if str(x).strip()])
    parts = []
    for item in re.split(r"[,;|/]+", raw):
        item = item.strip()
        if item and item.lower() not in {p.lower() for p in parts}:
            parts.append(item)
    return "; ".join(parts[:20])


def create_draft_from_submission(submission_id):
    sub_df = read_csv_safely(SUBMISSIONS_FILE, SUBMISSION_COLUMNS)
    if sub_df.empty or submission_id not in sub_df["submission_id"].tolist():
        return None, "Submission not found."
    sub = sub_df[sub_df["submission_id"] == submission_id].iloc[0]

    if str(sub.get("converted_opportunity_id", "")).strip():
        return sub.get("converted_opportunity_id"), "This submission has already been converted."

    opp_path = DATA_DIR / "opportunities.csv"
    req_path = DATA_DIR / "requirements.csv"
    path_path = DATA_DIR / "pathways.csv"

    opp_df = pd.read_csv(opp_path, dtype=str).fillna("")
    req_df = pd.read_csv(req_path, dtype=str).fillna("")
    path_df = pd.read_csv(path_path, dtype=str).fillna("")

    suffix = re.sub(r"[^A-Za-z0-9]", "", submission_id)[-8:].upper()
    opp_id = f"INTAKE-{suffix}"
    if opp_id in opp_df["opportunity_id"].tolist():
        opp_id = f"INTAKE-{suffix}-{uuid.uuid4().hex[:4].upper()}"

    primary_pop = "Yes" if "ug" in str(sub.get("target_student_level", "")).lower() or "undergraduate" in str(sub.get("target_student_level", "")).lower() else "Unclear"

    new_opp = {col: "" for col in opp_df.columns}
    new_opp.update(
        {
            "opportunity_id": opp_id,
            "title": compact(sub.get("opportunity_title", ""), "Untitled intake opportunity"),
            "opportunity_type": compact(sub.get("opportunity_type", ""), "Other / Not sure"),
            "global_node_id": compact(sub.get("global_node_id", ""), "GIC-FUTURE"),
            "global_index_type": compact(sub.get("global_index_type", ""), "Other / not sure"),
            "country": compact(sub.get("country", ""), "Not specified"),
            "city_region": compact(sub.get("city_region", ""), "Not specified"),
            "primary_discipline": compact(sub.get("primary_discipline", ""), "Interdisciplinary / not specified"),
            "student_level_eligibility": compact(sub.get("target_student_level", ""), "Macon UG primary; other students not excluded"),
            "primary_qep_population": primary_pop,
            "opportunity_stage": compact(sub.get("student_stage", ""), "Exploratory / validate before publication"),
            "short_description": compact(sub.get("short_description", ""), "Submitted through intake form; admin review needed."),
            "related_mercer_experiences": compact(sub.get("related_mercer_experiences", ""), "Related Mercer experience to be clarified"),
            "source_system": "Streamlit intake form",
            "source_record_id": submission_id,
            "handshake_url": "",
            "application_url": "",
            "mercer_owner": compact(sub.get("mercer_owner", ""), compact(sub.get("submitter_name", ""), "QEP admin")),
            "owner_unit": compact(sub.get("owner_unit", ""), compact(sub.get("submitter_unit", ""), "OGE / QEP")),
            "partner_org": compact(sub.get("partner_org", ""), "TBD partner"),
            "visibility_status": "Hidden",
            "admin_status": "Submitted",
            "initial_validator": "GIC Director / regional lead",
            "final_approver": "QEP Co-Directors",
            "last_validated_date": "",
            "next_review_due": next_review_date(),
            "annual_approval_deadline": annual_approval_deadline(),
            "record_confidence": "Unreviewed - submitter intake",
            "is_sample_record": "No",
            "tags": build_tags_from_submission(sub),
        }
    )
    opp_df = pd.concat([opp_df, pd.DataFrame([new_opp])], ignore_index=True)
    opp_df.to_csv(opp_path, index=False)

    req_rows = []
    req_templates = [
        ("Language", "Language preparation", sub.get("language_requirements", ""), "Preferred unless marked required"),
        ("Skill", "Skill preparation", sub.get("skill_requirements", ""), "Preferred unless marked required"),
        ("Experience", "Prior experience", sub.get("experience_requirements", ""), "Preferred unless marked required"),
        ("Evidence", "Expected proof/readiness evidence", sub.get("evidence_expected", ""), "Required for advising review"),
    ]
    for idx, (category, label, value, req_type) in enumerate(req_templates, start=1):
        if str(value).strip():
            req_rows.append(
                {
                    "requirement_id": f"REQ-{suffix}-{idx}",
                    "opportunity_id": opp_id,
                    "category": category,
                    "requirement_label": label,
                    "requirement_value": str(value).strip(),
                    "required_or_preferred": req_type,
                    "evidence_expected": compact(sub.get("evidence_expected", ""), "Self-attestation; advisor/faculty confirmation as needed"),
                    "match_use": "Yes",
                    "match_weight": "Medium",
                    "notes": "Auto-created from Streamlit intake. Admin should normalize before publication.",
                }
            )
    if req_rows:
        req_df = pd.concat([req_df, pd.DataFrame(req_rows)], ignore_index=True)
        req_df.to_csv(req_path, index=False)

    pathway_row = {col: "" for col in path_df.columns}
    pathway_row.update(
        {
            "pathway_id": f"PATH-{suffix}",
            "opportunity_id": opp_id,
            "global_node_id": compact(sub.get("global_node_id", ""), "GIC-FUTURE"),
            "pathway_stage": compact(sub.get("student_stage", ""), "Any stage / not sure"),
            "upstream_experience_type": "Study Abroad / MoM / GIC / local-global pathway",
            "upstream_experience_name": compact(sub.get("related_mercer_experiences", ""), "To be clarified during admin review"),
            "pathway_rationale": "Submitted as a globally indexed pathway lead. Admin should clarify how it builds from Mercer international or local-global learning.",
            "recommended_next_step": "Admin review, GIC Director initial validation, then QEP Co-Director approval before publication.",
            "support_unit": compact(sub.get("owner_unit", ""), compact(sub.get("submitter_unit", ""), "OGE / QEP")),
            "student_message": "This opportunity is in intake review and is not student-facing until approved.",
        }
    )
    path_df = pd.concat([path_df, pd.DataFrame([pathway_row])], ignore_index=True)
    path_df.to_csv(path_path, index=False)

    update_submission(
        submission_id,
        {
            "review_status": "Needs Review",
            "converted_opportunity_id": opp_id,
            "admin_notes": compact(sub.get("admin_notes", ""), "Converted to hidden draft opportunity record."),
        },
    )
    return opp_id, "Converted to hidden draft opportunity record."


def fit_for_profile(opp, reqs, profile):
    profile_text = combined_text(profile, [
        "student_type", "campus", "class_standing", "major", "minor", "completed_courses",
        "prior_global_experiences", "countries_regions", "languages", "prior_research",
        "prior_service", "prior_internships_jobs", "skills", "career_interests",
        "research_interests", "service_interests", "preferred_opportunity_types"
    ])
    opp_text = combined_text(opp, [
        "title", "opportunity_type", "global_node_id", "global_index_type", "country",
        "city_region", "primary_discipline", "short_description",
        "related_mercer_experiences", "tags"
    ])
    req_text = " ".join(reqs["requirement_value"].astype(str).tolist() + reqs["requirement_label"].astype(str).tolist()) if not reqs.empty else ""

    p = tokens(profile_text)
    o = tokens(opp_text + " " + req_text)
    overlaps = sorted(p.intersection(o))

    preferred_types = tokens(str(profile.get("preferred_opportunity_types", "")))
    type_tokens = tokens(str(opp.get("opportunity_type", "")))
    type_bonus = 2 if preferred_types.intersection(type_tokens) else 0

    region_bonus = 0
    profile_regions = tokens(str(profile.get("countries_regions", "")))
    opp_regions = tokens(str(opp.get("country", "")) + " " + str(opp.get("city_region", "")) + " " + str(opp.get("global_node_id", "")))
    if profile_regions.intersection(opp_regions):
        region_bonus = 2

    discipline_bonus = 0
    if tokens(str(profile.get("major", "")) + " " + str(profile.get("minor", ""))).intersection(tokens(str(opp.get("primary_discipline", "")))):
        discipline_bonus = 2

    score = len(overlaps) + type_bonus + region_bonus + discipline_bonus

    missing = []
    matched = []

    for _, r in reqs.iterrows():
        r_text = str(r["requirement_value"]) + " " + str(r["requirement_label"]) + " " + str(r["category"])
        overlap = tokens(r_text).intersection(p)
        label = str(r["requirement_label"])
        if overlap:
            matched.append(label)
        elif str(r["required_or_preferred"]).lower().startswith("required"):
            missing.append(label)

    if score >= 12 and len(missing) == 0:
        label = "Strong fit"
    elif score >= 7:
        label = "Possible fit"
    elif score >= 3:
        label = "Build readiness"
    else:
        label = "Explore with advisor"

    return label, overlaps[:12], matched[:8], missing[:8]


def opportunity_card(row, show_admin=False, profile=None):
    opp_id = row["opportunity_id"]
    reqs = requirements[requirements["opportunity_id"] == opp_id]
    pways = pathways[pathways["opportunity_id"] == opp_id]

    with st.container(border=True):
        col1, col2, col3 = st.columns([4, 2, 2])
        with col1:
            st.subheader(row["title"])
            st.caption(f'{row["opportunity_type"]} | {row["country"]} | {row["global_index_type"]}')
        with col2:
            st.metric("Node", row["global_node_id"])
        with col3:
            stage = row["opportunity_stage"] or "Not specified"
            st.write(f"**Stage:** {stage}")

        st.write(row["short_description"])

        if profile is not None:
            label, overlap, matched, missing = fit_for_profile(row, reqs, profile)
            st.markdown(f"**Fit guidance:** `{label}`")
            if overlap:
                st.write("**Matched signals:** " + ", ".join(overlap))
            if matched:
                st.write("**Requirements with evidence signals:** " + ", ".join(matched))
            if missing:
                st.warning("Build next: " + ", ".join(missing))

        if not pways.empty:
            with st.expander("Pathway explanation", expanded=False):
                for _, p in pways.iterrows():
                    st.write(f"**Student journey:** {p['pathway_stage']}")
                    st.write(p["pathway_rationale"])
                    st.write(f"**Recommended next step:** {p['recommended_next_step']}")
                    st.write(f"**Support unit:** {p['support_unit']}")

        if not reqs.empty:
            with st.expander("Requirements and evidence", expanded=False):
                st.dataframe(
                    reqs[["category", "requirement_label", "required_or_preferred", "evidence_expected"]],
                    use_container_width=True,
                    hide_index=True,
                )

        st.write(f"**Mercer support:** {row['mercer_owner']} ({row['owner_unit']})")
        if row.get("handshake_url"):
            st.write(f"**Handshake:** {row['handshake_url']}")
        if row.get("application_url"):
            st.write(f"**Apply / learn more:** {row['application_url']}")

        if show_admin:
            st.divider()
            st.write(f"**Admin status:** {row['admin_status']} | **Visibility:** {row['visibility_status']}")
            st.write(f"**Initial validator:** {row['initial_validator']} | **Final approver:** {row['final_approver']}")
            st.write(f"**Next review due:** {row['next_review_due']} | **Approval deadline:** {row['annual_approval_deadline']}")
            st.caption(f"Record confidence: {row['record_confidence']} | Sample record: {row['is_sample_record']}")


def filter_opportunities(df):
    st.sidebar.header("Search filters")
    node_options = ["All"] + [f"{r.global_node_id} - {r.global_node_name}" for _, r in nodes.sort_values("build_priority").iterrows()]
    node_choice = st.sidebar.selectbox("Global node", node_options, index=1)
    if node_choice != "All":
        node_id = node_choice.split(" - ")[0]
        df = df[df["global_node_id"] == node_id]

    type_options = ["All"] + sorted([x for x in df["opportunity_type"].unique() if x])
    type_choice = st.sidebar.selectbox("Opportunity type", type_options)
    if type_choice != "All":
        df = df[df["opportunity_type"] == type_choice]

    status_options = ["Student-facing approved only", "All prototype records", "Needs review / admin work"]
    status_choice = st.sidebar.radio("Visibility mode", status_options, index=1)
    if status_choice == "Student-facing approved only":
        df = df[df["admin_status"] == "Approved/Published"]
    elif status_choice == "Needs review / admin work":
        df = df[df["admin_status"].isin(["Needs Review", "Submitted", "CCPD Review Needed", "QEP Co-Director Approval Pending"])]

    q = st.sidebar.text_input("Keyword search", "")
    if q:
        q_lower = q.lower()
        searchable = df.apply(lambda r: " ".join(map(str, r.values)).lower(), axis=1)
        df = df[searchable.str.contains(q_lower, na=False)]

    return df


def render_submitter_form(node_id, default_country, key_prefix):
    config = NODE_FORM_CONFIG[node_id]
    st.subheader(config["label"])
    st.write(config["help"])
    st.caption("Faculty/staff submitters can provide what they know. Unknowns are acceptable; admin review will normalize and validate the record.")

    form_key = f"intake_form_{key_prefix}"
    with st.form(form_key, clear_on_submit=False):
        st.markdown("#### 1. About you")
        c1, c2 = st.columns(2)
        with c1:
            submitter_name = st.text_input("Your name", key=f"{key_prefix}_name")
            submitter_unit = st.text_input("Mercer unit / department", key=f"{key_prefix}_unit")
        with c2:
            submitter_email = st.text_input("Your Mercer email", key=f"{key_prefix}_email")
            submitter_role = st.selectbox(
                "Your role",
                ["Faculty lead", "GIC Director / regional lead", "OGE/QEP admin", "MoM lead", "CCPD / advisor", "Other Mercer faculty/staff"],
                key=f"{key_prefix}_role",
            )

        st.markdown("#### 2. Opportunity basics")
        opportunity_title = st.text_input("Opportunity title or working name", key=f"{key_prefix}_title")
        opportunity_type = st.selectbox("Opportunity type", OPPORTUNITY_TYPES, key=f"{key_prefix}_type")
        short_description = st.text_area(
            "Plain-language description",
            height=110,
            placeholder="Example: A summer research/service placement with a community partner focused on clean water education.",
            key=f"{key_prefix}_description",
        )
        c3, c4 = st.columns(2)
        with c3:
            partner_org = st.text_input("Partner organization, office, or sponsor", key=f"{key_prefix}_partner")
            primary_discipline = st.text_input("Relevant disciplines / majors", placeholder="Engineering; Education; Public Health", key=f"{key_prefix}_discipline")
        with c4:
            student_stage = st.selectbox("Best student journey stage", STUDENT_STAGE_OPTIONS, key=f"{key_prefix}_stage")
            target_student_level = st.text_input("Student audience", value="Macon UG primary; other students not excluded", key=f"{key_prefix}_level")

        st.markdown("#### 3. Global pathway connection")
        c5, c6, c7 = st.columns(3)
        with c5:
            country = st.text_input("Country", value=default_country, key=f"{key_prefix}_country")
        with c6:
            city_region = st.text_input("City / region / local site", key=f"{key_prefix}_city")
        with c7:
            global_index_type = st.selectbox("Global index type", GLOBAL_INDEX_TYPES, key=f"{key_prefix}_index")
        related_mercer_experiences = st.text_area(
            "What Mercer experience does this build from or prepare for?",
            height=90,
            placeholder="Example: DR clean water pathway; Greece migration/culture work; local-global service with adjacent population.",
            key=f"{key_prefix}_related",
        )

        st.markdown("#### 4. Student readiness and evidence")
        target_majors = st.text_input("Target majors/minors, if known", key=f"{key_prefix}_majors")
        language_requirements = st.text_input("Language expectations", placeholder="None; Spanish helpful; Greek not required", key=f"{key_prefix}_language")
        skill_requirements = st.text_area("Skills or preparation students should have", height=80, key=f"{key_prefix}_skills")
        experience_requirements = st.text_area("Prior experience students should have", height=80, key=f"{key_prefix}_experience")
        evidence_expected = st.text_area(
            "What evidence would help confirm readiness?",
            height=80,
            placeholder="Self-attestation, resume, informal transcript, faculty confirmation, portfolio, certificate, reflection, etc.",
            key=f"{key_prefix}_evidence",
        )

        st.markdown("#### 5. Logistics, contacts, and backup")
        c8, c9 = st.columns(2)
        with c8:
            compensation_funding = st.text_input("Compensation / funding / cost notes", key=f"{key_prefix}_funding")
            timing = st.text_input("Timing", placeholder="Summer; fall; rolling; not sure", key=f"{key_prefix}_timing")
            mercer_owner = st.text_input("Mercer owner or support person", value=submitter_name, key=f"{key_prefix}_owner")
        with c9:
            deadline = st.text_input("Application deadline or review timing", key=f"{key_prefix}_deadline")
            owner_unit = st.text_input("Owner/support unit", value=submitter_unit, key=f"{key_prefix}_owner_unit")
            partner_relationship_status = st.selectbox(
                "Relationship status",
                ["Known Mercer partner", "Faculty/staff contact", "Exploratory lead", "Handshake/import lead", "Not sure"],
                key=f"{key_prefix}_relationship",
            )
        c10, c11 = st.columns(2)
        with c10:
            partner_contact_name = st.text_input("Partner contact name, if known", key=f"{key_prefix}_partner_contact_name")
        with c11:
            partner_contact_email = st.text_input("Partner contact email, if known", key=f"{key_prefix}_partner_contact_email")
        backup_files = st.file_uploader(
            "Optional backup files for admin recordkeeping",
            accept_multiple_files=True,
            key=f"{key_prefix}_files",
            help="For the demo, uploaded files are stored with the local app data. Do not upload sensitive documents in a public demo.",
        )

        submitted = st.form_submit_button("Submit opportunity lead", use_container_width=True)

    if submitted:
        missing = []
        if not submitter_name.strip():
            missing.append("your name")
        if not submitter_email.strip():
            missing.append("your Mercer email")
        if not opportunity_title.strip():
            missing.append("opportunity title")
        if not short_description.strip():
            missing.append("plain-language description")
        if missing:
            st.error("Please add: " + ", ".join(missing) + ".")
            return

        submission_id = "SUB-" + datetime.utcnow().strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:6].upper()
        saved_files = save_uploaded_files(backup_files, submission_id)
        row = {
            "submission_id": submission_id,
            "submitted_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "submitter_name": submitter_name.strip(),
            "submitter_email": submitter_email.strip(),
            "submitter_unit": submitter_unit.strip(),
            "submitter_role": submitter_role,
            "global_node_id": node_id,
            "opportunity_title": opportunity_title.strip(),
            "opportunity_type": opportunity_type,
            "short_description": short_description.strip(),
            "country": country.strip(),
            "city_region": city_region.strip(),
            "global_index_type": global_index_type,
            "related_mercer_experiences": related_mercer_experiences.strip(),
            "student_stage": student_stage,
            "primary_discipline": primary_discipline.strip(),
            "target_student_level": target_student_level.strip(),
            "target_majors": target_majors.strip(),
            "language_requirements": language_requirements.strip(),
            "skill_requirements": skill_requirements.strip(),
            "experience_requirements": experience_requirements.strip(),
            "evidence_expected": evidence_expected.strip(),
            "compensation_funding": compensation_funding.strip(),
            "timing": timing.strip(),
            "deadline": deadline.strip(),
            "partner_org": partner_org.strip(),
            "partner_contact_name": partner_contact_name.strip(),
            "partner_contact_email": partner_contact_email.strip(),
            "partner_relationship_status": partner_relationship_status,
            "mercer_owner": mercer_owner.strip(),
            "owner_unit": owner_unit.strip(),
            "backup_files": saved_files,
            "review_status": "Submitted",
            "admin_notes": "",
            "converted_opportunity_id": "",
        }
        append_csv_row(SUBMISSIONS_FILE, SUBMISSION_COLUMNS, row)
        st.session_state["last_submission_id"] = submission_id
        st.session_state["last_submission_title"] = opportunity_title.strip()
        st.cache_data.clear()
        st.rerun()


def render_submission_queue():
    st.header("Submission queue and intake-to-database loop")
    st.write("This models how faculty/staff submissions become hidden draft database records before validation and publication.")

    current = read_csv_safely(SUBMISSIONS_FILE, SUBMISSION_COLUMNS)
    if current.empty:
        st.info("No submissions yet. Use the Submitter form tab to create a lead.")
        return

    counts = current["review_status"].value_counts().rename_axis("review_status").reset_index(name="count")
    st.dataframe(counts, use_container_width=True, hide_index=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        status_filter = st.multiselect(
            "Filter by review status",
            SUBMISSION_REVIEW_STATUSES,
            default=["Submitted", "Needs Review", "Needs Clarification"],
        )
    with c2:
        st.download_button(
            "Download submissions CSV",
            data=current.to_csv(index=False),
            file_name="qep_opportunity_submissions.csv",
            mime="text/csv",
            use_container_width=True,
        )

    visible = current[current["review_status"].isin(status_filter)] if status_filter else current.copy()
    summary_cols = [
        "submission_id",
        "submitted_at",
        "opportunity_title",
        "global_node_id",
        "opportunity_type",
        "submitter_name",
        "submitter_unit",
        "review_status",
        "converted_opportunity_id",
    ]
    st.dataframe(visible[summary_cols], use_container_width=True, hide_index=True)

    st.subheader("Review one submission")
    submission_ids = visible["submission_id"].tolist() or current["submission_id"].tolist()
    selected = st.selectbox("Submission ID", submission_ids)
    sub = current[current["submission_id"] == selected].iloc[0]

    left, right = st.columns([2, 1])
    with left:
        st.markdown(f"### {sub['opportunity_title']}")
        st.caption(f"{sub['opportunity_type']} | {sub['global_node_id']} | {sub['country']} | submitted by {sub['submitter_name']}")
        st.write(sub["short_description"])
        with st.expander("Full submitted record", expanded=True):
            detail = pd.DataFrame(
                [(col, sub.get(col, "")) for col in SUBMISSION_COLUMNS],
                columns=["field", "value"],
            )
            st.dataframe(detail, use_container_width=True, hide_index=True)
    with right:
        new_status = st.selectbox(
            "Set review status",
            SUBMISSION_REVIEW_STATUSES,
            index=SUBMISSION_REVIEW_STATUSES.index(sub["review_status"]) if sub["review_status"] in SUBMISSION_REVIEW_STATUSES else 0,
        )
        admin_notes = st.text_area("Admin notes", value=sub.get("admin_notes", ""), height=120)
        if st.button("Update submission status", use_container_width=True):
            update_submission(selected, {"review_status": new_status, "admin_notes": admin_notes})
            st.cache_data.clear()
            st.session_state["last_admin_action"] = f"Updated {selected} to {new_status}."
            st.rerun()

        already_converted = str(sub.get("converted_opportunity_id", "")).strip()
        if already_converted:
            st.success(f"Converted as {already_converted}.")
        else:
            if st.button("Convert to hidden draft opportunity", use_container_width=True):
                opp_id, message = create_draft_from_submission(selected)
                st.cache_data.clear()
                st.session_state["last_admin_action"] = f"{message} Opportunity ID: {opp_id}."
                st.rerun()

        st.warning("Conversion creates a hidden draft. It does not publish the record to the student-facing search mode.")


st.markdown(
    f"""
    <div style="border-left: 6px solid {ORANGE}; padding-left: 1rem;">
    <h1>Pathways to Purpose Opportunities MVP</h1>
    <p>Streamlit proof-of-concept for globally indexed, admin-approved independent opportunities.
    Dominican Republic is prioritized first; Greece second; Macon/US local-global pathways are modeled as a future-facing node.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state.get("last_submission_id"):
    st.success(
        f"Submission received: {st.session_state['last_submission_title']} "
        f"({st.session_state['last_submission_id']}). It is now in the admin queue."
    )
if st.session_state.get("last_admin_action"):
    st.success(st.session_state["last_admin_action"])

st.info(
    "Prototype note: seed records are synthetic or draft placeholders unless validated by the QEP Database and Visualization Working Group. "
    "The intake form is a demo of the population loop, not a production records system."
)

tab_submit, tab_queue, tab_search, tab_match, tab_advisor, tab_admin, tab_notes = st.tabs(
    [
        "Submitter form",
        "Submission queue",
        "Search",
        "Student profile match",
        "Advisor demo",
        "Admin review",
        "Data notes",
    ]
)

with tab_submit:
    st.header("Faculty/staff opportunity intake")
    st.write(
        "This is the lightweight in-app form model. It lets low-tech submitters enter a lead, upload backup files, "
        "and send the record into a review queue without using Microsoft Forms."
    )
    st.warning("For the public demo, do not upload confidential student records, passports, medical records, or other sensitive documents.")
    form_dr, form_gr, form_mcn, form_future = st.tabs(
        ["Dominican Republic", "Greece", "Macon / US local-global", "Other / future"]
    )
    with form_dr:
        render_submitter_form("GIC-DR", NODE_FORM_CONFIG["GIC-DR"]["country"], "dr")
    with form_gr:
        render_submitter_form("GIC-GR", NODE_FORM_CONFIG["GIC-GR"]["country"], "gr")
    with form_mcn:
        render_submitter_form("GIC-MCN", NODE_FORM_CONFIG["GIC-MCN"]["country"], "mcn")
    with form_future:
        render_submitter_form("GIC-FUTURE", NODE_FORM_CONFIG["GIC-FUTURE"]["country"], "future")

with tab_queue:
    render_submission_queue()

with tab_search:
    st.header("Search independent global opportunities")
    filtered = filter_opportunities(opportunities.copy())
    st.write(f"Showing **{len(filtered)}** records.")
    if filtered.empty:
        st.warning("No records match these filters. In P0, most records are hidden/draft until admin approval.")
    for _, row in filtered.iterrows():
        opportunity_card(row, show_admin=False)

with tab_match:
    st.header("Model a student profile match")
    profile_names = profiles["profile_name"].tolist()
    selected_profile_name = st.selectbox("Choose demo profile", profile_names)
    profile = profiles[profiles["profile_name"] == selected_profile_name].iloc[0]

    with st.expander("Profile summary", expanded=True):
        st.write(f"**Student type:** {profile['student_type']} | **Campus:** {profile['campus']} | **Class:** {profile['class_standing']}")
        st.write(f"**Major/minor:** {profile['major']} / {profile['minor']}")
        st.write(f"**Global experience/interests:** {profile['prior_global_experiences']} | {profile['countries_regions']}")
        st.write(f"**Skills:** {profile['skills']}")
        st.write(f"**Preferred opportunity types:** {profile['preferred_opportunity_types']}")

    candidate_df = opportunities[opportunities["global_node_id"].isin(["GIC-DR", "GIC-GR", "GIC-MCN"])].copy()
    scored = []
    for _, row in candidate_df.iterrows():
        reqs = requirements[requirements["opportunity_id"] == row["opportunity_id"]]
        label, overlap, matched, missing = fit_for_profile(row, reqs, profile)
        order = {"Strong fit": 0, "Possible fit": 1, "Build readiness": 2, "Explore with advisor": 3}.get(label, 4)
        scored.append((order, label, row))
    scored.sort(key=lambda x: x[0])

    for _, label, row in scored:
        opportunity_card(row, show_admin=False, profile=profile)

with tab_advisor:
    st.header("Advisor value demo")
    selected_profile_name = st.selectbox("Advisor profile", profiles["profile_name"].tolist(), key="advisor_profile")
    profile = profiles[profiles["profile_name"] == selected_profile_name].iloc[0]
    st.subheader("Suggested advising conversation")
    st.write("Use this view to explain why an opportunity appears, what readiness evidence exists, and what the student should build next.")
    advisor_rows = []
    for _, row in opportunities.iterrows():
        if row["global_node_id"] not in ["GIC-DR", "GIC-GR", "GIC-MCN"]:
            continue
        reqs = requirements[requirements["opportunity_id"] == row["opportunity_id"]]
        label, overlap, matched, missing = fit_for_profile(row, reqs, profile)
        advisor_rows.append({
            "fit_guidance": label,
            "opportunity_id": row["opportunity_id"],
            "title": row["title"],
            "node": row["global_node_id"],
            "type": row["opportunity_type"],
            "matched_signals": ", ".join(overlap[:6]),
            "build_next": ", ".join(missing[:4]) if missing else "Clarify next step with Mercer owner",
            "support_unit": row["owner_unit"],
        })
    advisor_df = pd.DataFrame(advisor_rows)
    if not advisor_df.empty:
        order = {"Strong fit": 0, "Possible fit": 1, "Build readiness": 2, "Explore with advisor": 3}
        advisor_df["sort"] = advisor_df["fit_guidance"].map(order).fillna(4)
        advisor_df = advisor_df.sort_values(["sort", "node"]).drop(columns=["sort"])
        st.dataframe(advisor_df, use_container_width=True, hide_index=True)

    st.warning("Persistent student saved/interested records are intentionally not enabled in P0. Add after search/filter has been tested with users.")

with tab_admin:
    st.header("Admin review prototype")
    st.write("This is a functional model of the workflow, not a production approval system.")
    admin_cols = [
        "opportunity_id", "title", "global_node_id", "opportunity_type", "visibility_status",
        "admin_status", "initial_validator", "final_approver", "next_review_due", "annual_approval_deadline"
    ]
    st.dataframe(opportunities[admin_cols], use_container_width=True, hide_index=True)

    st.subheader("Workflow states")
    st.dataframe(workflow, use_container_width=True, hide_index=True)

    with st.expander("View record detail"):
        selected_id = st.selectbox("Opportunity ID", opportunities["opportunity_id"].tolist())
        row = opportunities[opportunities["opportunity_id"] == selected_id].iloc[0]
        opportunity_card(row, show_admin=True)

with tab_notes:
    st.header("Data and governance notes")
    st.markdown(
        """
        **P0 now demonstrates three loops**
        - Submitter intake: faculty/staff can submit a lead using an in-app form.
        - Admin queue: the submission can be reviewed, annotated, and converted to a hidden draft database record.
        - Student/advisor discovery: approved or prototype records can be searched and matched.

        **P0 non-goals**
        - No live Mercer authentication.
        - No production storage guarantee for web deployment.
        - No real sensitive student records.
        - No official student transcript integration.
        - No live Handshake import.
        - No external partner portal.
        - No production approval workflow.

        **P0 goals**
        - Prove the search/filter experience.
        - Prove the DR/Greece pivot.
        - Prove how opportunity records connect to global pathways.
        - Prove advisor-facing match explanations.
        - Prove the submitter-to-admin-to-database loop.

        **Next phase**
        Add persistent storage and interest capture after the form/search interface is validated by focus groups.
        """
    )
