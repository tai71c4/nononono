async function getRecommendations() {
  const input = document.getElementById("userPreferences").value;
  const response = await fetch("/recommend-by-preferences", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ preferences: input })
  });
  const movies = await response.json();
  window.location.href = "/results?movies=" + encodeURIComponent(JSON.stringify(movies));
}