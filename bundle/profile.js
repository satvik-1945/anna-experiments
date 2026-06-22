/** Profile helpers + job role catalog (shipped with app for all users). */

let _catalog = null;

export async function loadJobCatalog() {
  if (_catalog) return _catalog;
  const res = await fetch("./data/job-catalog.json");
  if (!res.ok) throw new Error("Could not load job role catalog.");
  _catalog = await res.json();
  return _catalog;
}

export function findRole(catalog, roleId) {
  return catalog?.roles?.find((r) => r.id === roleId) || null;
}

let _resumeTemplate = null;
export async function loadResumeTemplate() {
  if (_resumeTemplate) return _resumeTemplate;
  const res = await fetch("./data/resume-template.tex");
  if (!res.ok) throw new Error("Could not load the starter resume template.");
  _resumeTemplate = await res.text();
  return _resumeTemplate;
}

export function populateRoleSelect(selectEl, catalog, selectedId) {
  if (!selectEl || !catalog?.roles) return;
  selectEl.innerHTML = '<option value="">— Select a role —</option>';
  for (const role of catalog.roles) {
    const opt = document.createElement("option");
    opt.value = role.id;
    opt.textContent = role.label;
    if (role.id === selectedId) opt.selected = true;
    selectEl.appendChild(opt);
  }
}

export function populateDomainSelect(selectEl, catalog, selectedDomain) {
  if (!selectEl || !catalog?.domains) return;
  selectEl.innerHTML = "";
  for (const [key, label] of Object.entries(catalog.domains)) {
    const opt = document.createElement("option");
    opt.value = key;
    opt.textContent = label;
    if (key === selectedDomain) opt.selected = true;
    selectEl.appendChild(opt);
  }
}

export function applyRoleToForm(form, role) {
  if (!form || !role) return;
  if (form.search_term) form.search_term.value = role.search_term || "";
  if (form.target_skills && role.skills?.length) {
    form.target_skills.value = role.skills.join(", ");
  }
  if (form.domain && role.domain) form.domain.value = role.domain;
  if (form.role_id) form.role_id.value = role.id;
}

export function isProfileComplete(profile) {
  if (!profile?.exists) return false;
  if (profile.profile_complete != null) return Boolean(profile.profile_complete);
  return Boolean(
    String(profile.name || "").trim()
    && String(profile.search_term || "").trim()
    && String(profile.resume_tex || "").trim()
    && (Array.isArray(profile.target_skills) ? profile.target_skills.length : String(profile.target_skills || "").trim()),
  );
}

export function fillProfileForm(form, profile, catalog) {
  if (!form) return;
  const p = profile || {};
  if (form.name) form.name.value = p.name || "";
  if (form.location) form.location.value = p.location || "India";
  if (form.search_term) form.search_term.value = p.search_term || "";
  if (form.target_skills) {
    form.target_skills.value = Array.isArray(p.target_skills)
      ? p.target_skills.join(", ")
      : p.target_skills || "";
  }
  if (form.domain && catalog) populateDomainSelect(form.domain, catalog, p.domain || "software_engineering");
  else if (form.domain && p.domain) form.domain.value = p.domain;
  if (form.seniority && p.seniority) form.seniority.value = p.seniority;
  if (form.years && p.years_experience != null) form.years.value = p.years_experience;
  if (form.latex) form.latex.value = p.resume_tex || "";

  if (form.role_id && catalog && p.search_term) {
    const match = catalog.roles.find(
      (r) => r.search_term.toLowerCase() === String(p.search_term).toLowerCase(),
    );
    if (match) form.role_id.value = match.id;
  }
}
