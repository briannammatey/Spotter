import { API, fetchJSON } from "../api.js";

export function renderChallenge(root) {
  root.innerHTML = `
    <div class="h1">NEW CHALLENGE</div>

    <label class="caption">ENTER CHALLENGE START DATE:</label>
    <input id="start" class="input-box" type="datetime-local"/>

    <label class="caption">ENTER CHALLENGE END DATE:</label>
    <input id="end" class="input-box" type="datetime-local"/>

    <label class="caption">WOULD YOU LIKE TO ATTACH ONE OF YOUR SAVED ROUTINES?</label>
    <div class="pills" id="attach">
      <button class="pill" data-value="yes">YES</button>
      <button class="pill" data-value="no">NO</button>
    </div>

    <div class="input-row">
      <div style="grid-column:1 / -1;">
        <label class="caption">ADD CHALLENGE GOAL</label>
        <input id="goal" class="input-box" placeholder="e.g., 10K steps daily"/>
      </div>
    </div>

    <label class="caption">ENTER CHALLENGE DESCRIPTION:</label>
    <textarea id="desc" class="input-box" rows="4" placeholder="ENTER DESCRIPTION HERE"></textarea>

    <label class="caption">INVITE FRIENDS</label>
    <div class="dropdown">
      <div class="dropdown-header"><span>INVITE FRIENDS</span><span class="chev">+</span></div>
      <div class="dropdown-list">
        <div class="dropdown-item">aaron</div>
        <div class="dropdown-item">bella</div>
        <div class="dropdown-item">carlos</div>
      </div>
    </div>

    <button class="cta" id="saveC">SAVE CHALLENGE</button>
  `;

  root.querySelector("#saveC").addEventListener("click", async () => {
    const payload = {
      title: "New Challenge",
      start: document.getElementById("start").value,
      end:   document.getElementById("end").value,
      goals: [document.getElementById("goal").value.trim()].filter(Boolean),
      invited: [],
      visibility: "public",
      desc:  document.getElementById("desc").value.trim()
    };
    try {
      await fetchJSON(`${API}/api/challenges`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify(payload)
      });
      alert("Challenge saved!");
    } catch (e) {
      alert("Error: " + e.message);
    }
  });
}
