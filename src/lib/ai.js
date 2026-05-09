export async function callAI(prompt, history = []) {
  try {
    const response = await fetch(
      "https://api.groq.com/openai/v1/chat/completions",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${import.meta.env.VITE_GROQ_API_KEY}`,
        },
        body: JSON.stringify({
          model: "llama-3.1-8b-instant",
          // you can also use:
          // "llama-3.1-70b-versatile"

          messages: [
            {
              role: "system",
              content:
                "You are HireBot, a professional career assistant helping users with jobs, CVs, interviews, and career guidance in a structured and concise way."
            },

            ...history.map((m) => ({
              role: m.role,
              content: m.content
            })),

            {
              role: "user",
              content: prompt
            }
          ],
          temperature: 0.7
        })
      }
    );

    const data = await response.json();

    console.log("🔥 GROQ RESPONSE:", data);

    if (!response.ok) {
      return `API ERROR: ${data?.error?.message || "Unknown error"}`;
    }

    return data?.choices?.[0]?.message?.content || "No response";
  } catch (err) {
    console.error("GROQ ERROR:", err);
    return "Network or API failure";
  }
}
