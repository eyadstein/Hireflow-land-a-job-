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

const MASTER_HARD_SKILLS = Object.keys(HARD_SKILLS_DICT);
const MASTER_SOFT_SKILLS = Object.keys(SOFT_SKILLS_DICT);

export function recommendJobs(resumeText = "", jobs = []) {
  const cleanResume = String(resumeText).toLowerCase();

  if (!cleanResume || !Array.isArray(jobs)) return [];

  const candidate = buildCandidateProfile(cleanResume);

  const eligibleJobs = jobs.filter((job) =>
    isEligibleDomain(candidate.domain, job.domain)
  );

  const pool = eligibleJobs.length >= 3 ? eligibleJobs : jobs;

  const scored = pool.map((job) => {
    const jdHardSkills = Array.isArray(job.hard_skills) ? job.hard_skills : [];
    const jdSoftSkills = Array.isArray(job.soft_skills) ? job.soft_skills : [];

    const jdHardVector = vectorizeSkills(jdHardSkills, MASTER_HARD_SKILLS);
    const jdSoftVector = vectorizeSkills(jdSoftSkills, MASTER_SOFT_SKILLS);

    const match = computeMatchFeatures(
      candidate.hardVector,
      jdHardVector,
      candidate.softVector,
      jdSoftVector
    );

    const titleScore = scoreTitle(job.title || "", candidate);
    const descriptionScore = scoreDescription(job.description || "", candidate);
    const domainScore = scoreDomain(candidate.domain, job.domain);

    const finalScore = Math.round(
      match.hardMatchRatio * 100 * 0.50 +
      match.softMatchRatio * 100 * 0.10 +
      titleScore * 0.15 +
      descriptionScore * 0.10 +
      domainScore * 0.15
    );

    return {
      ...job,
      matchScore: finalScore,
      matchedHardSkills: match.matchedHardSkills,
      matchedSoftSkills: match.matchedSoftSkills,
      missingHardSkills: match.missingHardSkills,
      missingSoftSkills: match.missingSoftSkills,
      hardMatchRatio: Math.round(match.hardMatchRatio * 100),
      softMatchRatio: Math.round(match.softMatchRatio * 100),
    };
  });

  return dedupeByTitle(
    scored
      .filter((job) => job.matchScore > 0)
      .sort((a, b) => b.matchScore - a.matchScore)
  ).slice(0, 5);
}

function buildCandidateProfile(text) {
  const hardSkills = extractSkillsFromText(text, HARD_SKILLS_DICT);
  const softSkills = extractSkillsFromText(text, SOFT_SKILLS_DICT);

  const hardVector = vectorizeSkills(hardSkills, MASTER_HARD_SKILLS);
  const softVector = vectorizeSkills(softSkills, MASTER_SOFT_SKILLS);

  return {
    hardSkills,
    softSkills,
    hardVector,
    softVector,
    domain: inferCandidateDomain(text, hardSkills),
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

function inferCandidateDomain(text, hardSkills) {
  const t = String(text).toLowerCase();
  const hs = new Set(hardSkills);

  if (
    hs.has("ai") ||
    hs.has("machine learning") ||
    hs.has("robotics") ||
    hs.has("arduino") ||
    t.includes("ai student")
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
    t.includes("instructor") ||
    t.includes("teaching") ||
    t.includes("mentor") ||
    t.includes("workshop") ||
    t.includes("tutorial")
  ) {
    return "education";
  }

  return "other";
}

function isEligibleDomain(candidateDomain, jobDomain) {
  if (candidateDomain === "ai-data") {
    return ["ai-data", "technical", "education"].includes(jobDomain);
  }

  if (candidateDomain === "technical") {
    return ["technical", "ai-data", "education"].includes(jobDomain);
  }

  if (candidateDomain === "education") {
    return ["education", "technical", "ai-data"].includes(jobDomain);
  }

  return true;
}

function scoreDomain(candidateDomain, jobDomain) {
  if (candidateDomain === jobDomain) return 100;

  if (
    (candidateDomain === "ai-data" && jobDomain === "technical") ||
    (candidateDomain === "technical" && jobDomain === "ai-data")
  ) {
    return 80;
  }

  if (
    (candidateDomain === "technical" && jobDomain === "education") ||
    (candidateDomain === "education" && jobDomain === "technical") ||
    (candidateDomain === "ai-data" && jobDomain === "education")
  ) {
    return 60;
  }

  return 0;
}

function scoreTitle(title, candidate) {
  const t = String(title).toLowerCase();
  let score = 0;

  candidate.hardSkills.forEach((skill) => {
    if (t.includes(skill)) score += 20;
  });

  if (
    candidate.domain === "technical" &&
    containsAny(t, ["developer", "engineer", "it", "technical", "qa"])
  ) {
    score += 40;
  }

  if (
    candidate.domain === "ai-data" &&
    containsAny(t, ["ai", "machine learning", "data", "python", "engineering"])
  ) {
    score += 40;
  }

  if (
    candidate.domain === "education" &&
    containsAny(t, ["instructor", "trainer", "mentor", "coach"])
  ) {
    score += 40;
  }

  return Math.min(score, 100);
}

function scoreDescription(description, candidate) {
  const d = String(description).toLowerCase();
  let score = 0;

  candidate.hardSkills.forEach((skill) => {
    if (d.includes(skill)) score += 8;
  });

  candidate.softSkills.forEach((skill) => {
    if (d.includes(skill)) score += 3;
  });

  return Math.min(score, 100);
}

function dedupeByTitle(jobs) {
  const seen = new Set();
  const out = [];

  for (const job of jobs) {
    const norm = String(job.title || "").toLowerCase().trim();
    if (!seen.has(norm)) {
      seen.add(norm);
      out.push(job);
    }
  }

  return out;
}

function containsAny(text, terms) {
  return terms.some((term) => text.includes(term));
}
