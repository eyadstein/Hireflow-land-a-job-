const HARD_SKILLS_DICT = {
  python: ["python"],
  java: ["java"],
  cpp: ["c++", "c/c++", "c programming"],
  arduino: ["arduino"],
  ai: ["ai", "artificial intelligence"],
  "machine learning": ["machine learning", "ml"],
  robotics: ["robotics", "robot"],
  "software development": ["software development", "software", "coding", "programming"],
  "backend development": ["backend", "backend development"],
  "web development": ["web development", "web"],
  "data analysis": ["data analysis", "analysis", "analytics"],
  "data science": ["data science"],
  testing: ["testing", "qa", "quality assurance"],
  networking: ["networking", "network"],
  "cloud computing": ["cloud", "cloud computing"],
  "project management": ["project management", "project", "projects"],
  "microsoft office": ["excel", "powerpoint", "word", "ms office", "microsoft office"],
  "ethical hacking": ["ethical hacking", "cybersecurity", "security"],
  engineering: ["engineering", "engineer"],
  "it support": ["it support", "technical support"],
};

const SOFT_SKILLS_DICT = {
  communication: ["communication", "communicator"],
  leadership: ["leadership", "leader", "representative"],
  teamwork: ["teamwork", "team player", "team"],
  "problem solving": ["problem solving", "problem-solving"],
  mentoring: ["mentor", "mentoring", "coaching", "teaching", "instructor"],
  adaptability: ["adaptability", "adaptable", "learning"],
  creativity: ["creativity", "creative"],
  organization: ["organization", "organizer", "organizing"],
  support: ["support"],
  "customer service": ["customer service", "customer focus"],
};

export function processJob(rawJob = {}) {
  const title = String(rawJob.job_title || rawJob.title || "").trim();
  const company = String(rawJob.company_name || "").trim();
  const location = String(rawJob.location || "").trim();
  const jobType = String(rawJob.job_type || "").trim();
  const careerLevel = String(rawJob.career_level || "").trim();
  const description = String(rawJob.job_description || "").trim();
  const requirements = String(rawJob.requirements || rawJob.qualifications || "").trim();
  const yearsExperience = String(rawJob.years_experience || "").trim();
  const education = String(rawJob.education || "").trim();
  const jobUrl = String(rawJob.job_url || "").trim();
  const source = String(rawJob.source || "").trim();

  const combinedText =
    `${title} ${description} ${requirements} ${education}`.toLowerCase();

  const hardSkills = extractSkillsFromText(combinedText, HARD_SKILLS_DICT);
  const softSkills = extractSkillsFromText(combinedText, SOFT_SKILLS_DICT);
  const allSkills = [...new Set([...hardSkills, ...softSkills])];

  return {
    job_title: title,
    company_name: company,
    location,
    job_type: jobType,
    career_level: careerLevel,
    job_description: description,
    requirements,
    years_experience: yearsExperience,
    education,
    job_url: jobUrl,
    source,
    hard_skills: hardSkills,
    soft_skills: softSkills,
    all_skills: allSkills,
    job_family: inferJobFamily(title, description, requirements, hardSkills, softSkills),
    is_processed: true,
    processed_at: new Date().toISOString(),
  };
}

export function processJobs(rawJobs = []) {
  return rawJobs.map(processJob);
}

function extractSkillsFromText(text, skillDict) {
  const found = [];

  for (const [canonical, variants] of Object.entries(skillDict)) {
    if (variants.some((variant) => text.includes(variant.toLowerCase()))) {
      found.push(canonical.toLowerCase());
    }
  }

  return found;
}

function inferJobFamily(title, description, requirements, hardSkills = [], softSkills = []) {
  const text =
    `${title} ${description} ${requirements} ${hardSkills.join(" ")} ${softSkills.join(" ")}`.toLowerCase();

  if (
    containsAny(text, [
      "ai", "artificial intelligence", "machine learning", "data science",
      "deep learning", "robotics", "arduino", "python", "computer vision", "nlp",
    ])
  ) {
    return "ai-data";
  }

  if (
    containsAny(text, [
      "developer", "software", "frontend", "backend", "programming", "java",
      "c++", "it support", "technical", "quality assurance", "qa",
      "information technology", "engineer", "engineering", "systems", "network", "technology",
    ])
  ) {
    return "technical";
  }

  if (
    containsAny(text, [
      "instructor", "trainer", "teaching", "education", "workshop",
      "tutorial", "mentor", "coaching", "ambassador",
    ])
  ) {
    return "education";
  }

  if (
    containsAny(text, [
      "marketing", "sales", "retail", "store manager", "sales assistant",
      "customer service", "collector", "business development", "future leaders program",
    ])
  ) {
    return "business";
  }

  if (
    containsAny(text, [
      "admin", "assistant", "receptionist", "administrative", "office",
      "coordinator", "document controller",
    ])
  ) {
    return "admin";
  }

  if (
    containsAny(text, [
      "accounting", "finance", "financial", "accounts", "banking", "investment",
    ])
  ) {
    return "finance";
  }

  if (
    containsAny(text, ["designer", "interior", "creative", "graphics", "ui", "ux", "ikea"])
  ) {
    return "creative";
  }

  return "other";
}

function containsAny(text, terms) {
  return terms.some((term) => text.includes(term));
}
