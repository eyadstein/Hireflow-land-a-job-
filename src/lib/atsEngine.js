const HARD_SKILLS_DICT = {
  python: ["python"],
  java: ["java"],
  cpp: ["c++", "c/c++"],
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

const MASTER_HARD_SKILLS = Object.keys(HARD_SKILLS_DICT);
const MASTER_SOFT_SKILLS = Object.keys(SOFT_SKILLS_DICT);

export function calculateATS(resumeText = "", job = {}) {
  const text = String(resumeText).toLowerCase();

  const cvHardSkills = extractSkillsFromText(text, HARD_SKILLS_DICT);
  const cvSoftSkills = extractSkillsFromText(text, SOFT_SKILLS_DICT);

  const cvHardVector = vectorizeSkills(cvHardSkills, MASTER_HARD_SKILLS);
  const cvSoftVector = vectorizeSkills(cvSoftSkills, MASTER_SOFT_SKILLS);

  const jdHardSkills = Array.isArray(job.hard_skills) ? job.hard_skills : [];
  const jdSoftSkills = Array.isArray(job.soft_skills) ? job.soft_skills : [];

  const jdHardVector = vectorizeSkills(jdHardSkills, MASTER_HARD_SKILLS);
  const jdSoftVector = vectorizeSkills(jdSoftSkills, MASTER_SOFT_SKILLS);

  const match = computeMatchFeatures(
    cvHardVector,
    jdHardVector,
    cvSoftVector,
    jdSoftVector
  );

  const education = String(job.education || "").toLowerCase().trim();
  let educationScore = 0.5;

  if (education) {
    if (
      (education.includes("bachelor") &&
        (text.includes("bachelor") ||
          text.includes("student") ||
          text.includes("university") ||
          text.includes("computer science") ||
          text.includes("information technology"))) ||
      (education.includes("master") && text.includes("master")) ||
      text.includes(education)
    ) {
      educationScore = 1;
    }
  }

  const expRequired = Number(job.years_experience);
  let experienceScore = 0.5;

  if (!Number.isNaN(expRequired)) {
    if (expRequired === 0) {
      experienceScore = 1;
    } else {
      const numbers = text.match(/\d+/g) || [];
      const likelyMatch = numbers.some((n) => {
        const v = Number(n);
        return v <= 10 && Math.abs(v - expRequired) <= 1;
      });

      experienceScore = likelyMatch ? 1 : 0.4;
    }
  }

  const finalScore = Math.round(
    match.hardMatchRatio * 100 * 0.65 +
    match.softMatchRatio * 100 * 0.05 +
    educationScore * 100 * 0.10 +
    experienceScore * 100 * 0.20
  );

  return {
    score: finalScore,
    matched: [...match.matchedHardSkills, ...match.matchedSoftSkills],
    missing: [...match.missingHardSkills, ...match.missingSoftSkills],
    matchedHard: match.matchedHardSkills,
    matchedSoft: match.matchedSoftSkills,
    missingHard: match.missingHardSkills,
    missingSoft: match.missingSoftSkills,
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

function vectorizeSkills(skills, masterList) {
  const skillSet = new Set((skills || []).map((s) => String(s).toLowerCase()));
  return masterList.map((skill) => (skillSet.has(skill.toLowerCase()) ? 1 : 0));
}

function computeMatchFeatures(cvHardVec, jdHardVec, cvSoftVec, jdSoftVec) {
  const matchedHardSkills = [];
  const missingHardSkills = [];
  const matchedSoftSkills = [];
  const missingSoftSkills = [];

  let matchedHard = 0;
  let requiredHard = jdHardVec.reduce((a, b) => a + b, 0);

  for (let i = 0; i < jdHardVec.length; i++) {
    if (jdHardVec[i] === 1 && cvHardVec[i] === 1) {
      matchedHard++;
      matchedHardSkills.push(MASTER_HARD_SKILLS[i]);
    } else if (jdHardVec[i] === 1 && cvHardVec[i] === 0) {
      missingHardSkills.push(MASTER_HARD_SKILLS[i]);
    }
  }

  let matchedSoft = 0;
  let requiredSoft = jdSoftVec.reduce((a, b) => a + b, 0);

  for (let i = 0; i < jdSoftVec.length; i++) {
    if (jdSoftVec[i] === 1 && cvSoftVec[i] === 1) {
      matchedSoft++;
      matchedSoftSkills.push(MASTER_SOFT_SKILLS[i]);
    } else if (jdSoftVec[i] === 1 && cvSoftVec[i] === 0) {
      missingSoftSkills.push(MASTER_SOFT_SKILLS[i]);
    }
  }

  return {
    hardMatchRatio: requiredHard ? matchedHard / requiredHard : 0,
    softMatchRatio: requiredSoft ? matchedSoft / requiredSoft : 0,
    matchedHardSkills,
    missingHardSkills,
    matchedSoftSkills,
    missingSoftSkills,
  };
}
