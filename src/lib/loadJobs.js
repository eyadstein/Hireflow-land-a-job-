import Papa from "papaparse";

export async function loadJobs() {
  const res = await fetch("/job_descriptions.csv");

  if (!res.ok) {
    throw new Error("Failed to load job_descriptions.csv");
  }

  const csvText = await res.text();

  const parsed = Papa.parse(csvText, {
    header: true,
    skipEmptyLines: true,
    transformHeader: (header) => header.trim(),
  });

  if (parsed.errors?.length) {
    console.error("CSV Parse Errors:", parsed.errors);
  }

  return parsed.data
    .map((job, index) => {
      const title = String(job.job_title || "").trim();
      const category = String(job.job_category || "").trim();
      const jobType = String(job.job_type || "").trim();
      const careerLevel = String(job.career_level || "").trim();
      const yearsExperience = String(job.years_experience || "").trim();
      const education = String(job.education || "").trim();
      const description = String(job.job_description || "").trim();
      const location = String(job.location || "").trim();

      const hardSkills = parseSkillArray(job.hard_skills);
      const softSkills = parseSkillArray(job.soft_skills);
      const allSkills = unique([
        ...hardSkills,
        ...softSkills,
        ...parseSkillArray(job.all_skills),
      ]);

      return {
        id: index + 1,
        title,
        category,
        job_type: jobType,
        career_level: careerLevel,
        years_experience: yearsExperience,
        education,
        description,
        location,
        hard_skills: hardSkills,
        soft_skills: softSkills,
        all_skills: allSkills,
        domain: inferDomain(title, category, description, hardSkills, softSkills),
      };
    })
    .filter((job) => job.title);
}

function parseSkillArray(value) {
  if (!value) return [];

  try {
    const cleaned = String(value).replace(/'/g, '"');
    const parsed = JSON.parse(cleaned);

    if (Array.isArray(parsed)) {
      return parsed.map((s) => String(s).trim().toLowerCase()).filter(Boolean);
    }

    return [];
  } catch {
    return String(value)
      .split("|")
      .map((s) => s.trim().toLowerCase())
      .filter(Boolean);
  }
}

function unique(arr) {
  return [...new Set(arr.filter(Boolean))];
}

function inferDomain(title, category, description, hardSkills = [], softSkills = []) {
  const text =
    `${title} ${category} ${description} ${hardSkills.join(" ")} ${softSkills.join(" ")}`.toLowerCase();

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
