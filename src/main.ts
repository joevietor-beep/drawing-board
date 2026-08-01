import "./styles.css";
import risingEntrepreneur from "../Architecture/Rising Entrepreneur.png";

type SectionId = "sanctuary" | "board-room" | "studio";
type View = "home" | "section" | "tool" | "meditation";

type Tool = { title: string; description: string; label: string };
type Section = { title: string; heading: string; description: string; tools: Tool[] };

const sections: Record<SectionId, Section> = {
  sanctuary: { title: "Sanctuary", heading: "Begin with awareness.", description: "A quiet room to arrive before the work begins.", tools: [
    { title: "Morning Meditation", description: "A guided moment to settle, notice, and choose an intention.", label: "Practice" },
    { title: "Journal", description: "Make space for what is present and what matters today.", label: "Reflect" },
    { title: "Constitution", description: "Return to the principles that hold the work together.", label: "Ground" },
  ] },
  "board-room": { title: "Board Room", heading: "Make the important moves visible.", description: "A clear room for commitments, conversations, and work in motion.", tools: [
    { title: "Today's Focus", description: "Must Do · Waiting On · Wins", label: "Plan" },
    { title: "DealDocs", description: "Recent conversations · Follow-ups · Pipeline", label: "Relationships" },
    { title: "Prospect Radar", description: "Yellow Pages · Apollo · LinkedIn · Lead imports", label: "Prospecting" },
    { title: "Analytics", description: "Calls made · Response rate · Website traffic · Revenue trends", label: "Measure" },
    { title: "Projects", description: "WordPress sites · Client work · Internal development", label: "Build" },
  ] },
  studio: { title: "Studio", heading: "Turn the work into something shareable.", description: "A focused collection of creative tools and working surfaces.", tools: [
    { title: "Article Architect", description: "Long-form writing.", label: "Write" },
    { title: "Social Vibe", description: "Facebook · LinkedIn · Instagram · X", label: "Publish" },
    { title: "Image Roll", description: "Prompt library · Editorial images · Hero graphics", label: "Create" },
    { title: "Video Edits", description: "Shotcut · DaVinci · Captions · Shorts", label: "Edit" },
    { title: "Plan Notes", description: "Whiteboard · Brainstorming · Mind maps · Meeting notes", label: "Think" },
  ] },
};

let view: View = "home";
let sectionId: SectionId | null = null;
let tool: Tool | null = null;
let meditationStep = 0;
const app = document.querySelector<HTMLDivElement>("#app");

function header() {
  const room = sectionId ? sections[sectionId].title : "A deliberate workspace";
  return `<header class="topbar"><button class="brand" data-action="home"><b>DB</b>Drawing Board</button><span class="chapter">${room}</span><button class="quiet" data-action="meditation">Morning meditation ↗</button></header>`;
}

function home() {
  return `<main class="home"><section class="intro"><p class="eyebrow">One chapter. One room. One careful stone at a time.</p><h1>A place to see the whole of your work.</h1><p>Enter through the room that serves this moment.</p></section><section class="rooms"><button class="room sanctuary" data-section="sanctuary"><img src="${risingEntrepreneur}" alt="Sunrise in a mountain landscape" /><span><small>Sanctuary</small><strong>Begin with awareness.</strong><em>Meditation · Journal · Constitution</em></span></button><button class="room boardroom" data-section="board-room"><span><small>Board Room</small><strong>Bring the day into focus.</strong><em>Priorities · Pipeline · Projects</em></span></button><button class="room studio" data-section="studio"><span><small>Studio</small><strong>Make something useful.</strong><em>Writing · Images · Video · Notes</em></span></button></section></main>`;
}

function section() {
  const room = sections[sectionId!];
  return `<main class="page"><button class="back" data-action="home">← All rooms</button><section class="heading"><p class="eyebrow">${room.title}</p><h1>${room.heading}</h1><p>${room.description}</p></section><section class="tool-grid">${room.tools.map((entry, index) => `<button class="tool" data-tool="${entry.title}"><small>0${index + 1}</small><i>${entry.label}</i><strong>${entry.title}</strong><p>${entry.description}</p><b>↗</b></button>`).join("")}</section></main>`;
}

function meditation() {
  const steps = [["Arrive", "Let the day wait at the door. Notice where you are."], ["Breathe", "Take three unhurried breaths. There is nothing to solve yet."], ["Notice", "What is asking for your attention beneath the noise?"], ["Intend", "Name one way you want to show up in the next chapter."]];
  const [title, copy] = steps[meditationStep];
  return `<main class="meditation"><img src="${risingEntrepreneur}" alt="" /><div class="wash"></div><button class="close" data-action="section">Close</button><section class="meditation-card"><p class="eyebrow">Morning meditation · ${meditationStep + 1} of ${steps.length}</p><h1>${title}</h1><p>${copy}</p><div class="progress"><span style="width:${(meditationStep + 1) * 25}%"></span></div><div class="actions"><button data-action="previous" ${meditationStep === 0 ? "disabled" : ""}>Back</button><button class="continue" data-action="next">${meditationStep === 3 ? "Complete" : "Continue"} →</button></div></section></main>`;
}

function toolView() {
  if (tool?.title === "Article Architect") {
    const draft = localStorage.getItem("drawing-board.article-draft") ?? "";
    return `<main class="page article"><button class="back" data-action="section">← Studio</button><p class="eyebrow">Write</p><h1>Article Architect</h1><p>A focused surface for your next long-form idea.</p><label for="draft">Working draft</label><textarea id="draft" placeholder="Start with the idea you want to make clear…">${draft}</textarea><small>Saved locally as you write.</small></main>`;
  }
  return `<main class="page placeholder"><button class="back" data-action="section">← ${sections[sectionId!].title}</button><div><p class="eyebrow">${tool?.label ?? "Workspace"}</p><h1>${tool?.title}</h1><p>${tool?.description}</p><hr /><p>This is a focused placeholder in the broad-strokes release. Its dedicated workflow and outside connections can be added one tool at a time.</p></div></main>`;
}

function render() {
  if (!app) return;
  const content = view === "home" ? home() : view === "section" ? section() : view === "meditation" ? meditation() : toolView();
  app.innerHTML = `${header()}${content}`;
  app.querySelectorAll<HTMLElement>("[data-section]").forEach((element) => element.onclick = () => { sectionId = element.dataset.section as SectionId; view = "section"; render(); });
  app.querySelectorAll<HTMLElement>("[data-tool]").forEach((element) => element.onclick = () => { tool = sections[sectionId!].tools.find((entry) => entry.title === element.dataset.tool) ?? null; view = tool?.title === "Morning Meditation" ? "meditation" : "tool"; render(); });
  app.querySelector<HTMLElement>("[data-action='home']")?.addEventListener("click", () => { view = "home"; sectionId = null; tool = null; render(); });
  app.querySelector<HTMLElement>("[data-action='section']")?.addEventListener("click", () => { view = sectionId ? "section" : "home"; tool = null; render(); });
  app.querySelector<HTMLElement>("[data-action='meditation']")?.addEventListener("click", () => { sectionId = "sanctuary"; tool = sections.sanctuary.tools[0]; meditationStep = 0; view = "meditation"; render(); });
  app.querySelector<HTMLElement>("[data-action='previous']")?.addEventListener("click", () => { meditationStep = Math.max(0, meditationStep - 1); render(); });
  app.querySelector<HTMLElement>("[data-action='next']")?.addEventListener("click", () => { if (meditationStep === 3) { tool = null; view = "section"; } else meditationStep += 1; render(); });
  app.querySelector<HTMLTextAreaElement>("#draft")?.addEventListener("input", (event) => localStorage.setItem("drawing-board.article-draft", (event.target as HTMLTextAreaElement).value));
}

render();
