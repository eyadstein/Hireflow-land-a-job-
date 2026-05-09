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

export function processResume(resumeText = "") {
  const text = String(resumeText).toLowerCase();

  const hardSkills = extractSkillsFromText(text, HARD_SKILLS_DICT);
  const softSkills = extractSkillsFromText(text, SOFT_SKILLS_DICT);

  return {
    raw_text: resumeText,
    hard_skills: hardSkills,
    soft_skills: softSkills,
    all_skills: [...new Set([...hardSkills, ...softSkills])],
    candidate_family: inferCandidateFamily(text, hardSkills),
  };
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

function inferCandidateFamily(text, hardSkills = []) {
  const hs = new Set(hardSkills);

  if (
    hs.has("ai") ||
    hs.has("machine learning") ||
    hs.has("robotics") ||
    hs.has("arduino") ||
    text.includes("ai student")
  ) {
    return "ai-data";
  }

  if (
    hs.has("python") ||
    hs.has("java") ||
    hs.has("cpp") ||
    hs.has("software development") ||
    hs.has("backend development") ||
    hs.has("web development") ||
    hs.has("it support") ||
    hs.has("engineering")
  ) {
    return "technical";
  }

  if (
    text.includes("instructor") ||
    text.includes("teaching") ||
    text.includes("mentor") ||
    text.includes("workshop") ||
    text.includes("tutorial")
  ) {
    return "education";
  }

  return "other";
}
