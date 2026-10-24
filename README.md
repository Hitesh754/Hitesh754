<!--
  Profile README for github.com/Hitesh754/Hitesh754
  Files: README.md (this file) + assets/banner.svg
  Maintenance: edit the text panel, project tables and the open-source table below.
  Add merged upstream PRs to the table in "~/open-source" as they happen.
-->

<p align="center">
  <img src="assets/banner.svg" alt="Terminal window: whoami — Hitesh Choudhary, software developer, systems tinkerer, AI/ML explorer" width="100%">
</p>

```text
hitesh@github
─────────────
role        software developer · systems tinkerer · AI/ML explorer
stage       third-year Computer Science Engineering student
runs on     Linux · Omarchy / Hyprland · Quickshell
building    full-stack apps · applied ML · developer tooling
exploring   Caelestia Shell (QML/Quickshell) · ToolJet
open to     internships · open-source collaboration
```

<p align="center">
  <a href="#projects">projects</a> ·
  <a href="#open-source">open source</a> ·
  <a href="#stack">stack</a> ·
  <a href="#activity">activity</a> ·
  <a href="#contact">contact</a>
</p>

---

## ~/projects

Four projects I'd point you to, with the honest scope of each.

### 01 · omarchy-caelestia

**The Caelestia desktop shell, integrated into Omarchy without replacing it.**

<table>
  <tr>
    <td width="110" valign="top"><b>problem</b></td>
    <td>Omarchy ships its own shell. Caelestia offers a richer Quickshell-based one (bar, dashboard, launcher, OSD, notifications). Running it on Omarchy means leaving the system layer alone.</td>
  </tr>
  <tr>
    <td valign="top"><b>interesting</b></td>
    <td>Omarchy stays the system layer; Caelestia is the visual layer on top. The installer builds into the user's directory, stages and activates transactionally, verifies startup, and restores the previous install if it fails. A theme hook converts the active Omarchy theme into Caelestia's colour scheme live.</td>
  </tr>
  <tr>
    <td valign="top"><b>stack</b></td>
    <td>Bash installers and hooks · Hyprland · Quickshell · QML/C++ (upstream shell) · CMake</td>
  </tr>
  <tr>
    <td valign="top"><b>focus</b></td>
    <td>Safe install / update / rollback, keeping a clean boundary between system and user layers, bridging themes. In progress: deriving the palette from the wallpaper.</td>
  </tr>
  <tr>
    <td valign="top"><b>credit</b></td>
    <td>Based on <a href="https://github.com/caelestia-dots">Caelestia Shell by caelestia-dots</a> (GPL-3.0). The shell and its commit history are upstream's; this repo adds the Omarchy integration layer in <code>omarchy/</code>.</td>
  </tr>
  <tr>
    <td valign="top"><b>links</b></td>
    <td><a href="https://github.com/Hitesh754/omarchy-caelestia">repository →</a> (branch <code>omarchy-integration</code>)</td>
  </tr>
</table>

### 02 · PlaylistKit

**Pull a playlist from any major platform into one clean, exportable form.**

<table>
  <tr>
    <td width="110" valign="top"><b>problem</b></td>
    <td>Playlists are locked inside separate services. PlaylistKit extracts track lists from Spotify, Apple Music, JioSaavn and YouTube, exports them as CSV, and batch-converts audio with metadata and cover art.</td>
  </tr>
  <tr>
    <td valign="top"><b>interesting</b></td>
    <td>Platform-specific extractors sit behind one FastAPI service. A matcher maps Spotify and Apple Music tracks to YouTube sources, and cover art from iTunes is embedded with ID3 tags.</td>
  </tr>
  <tr>
    <td valign="top"><b>stack</b></td>
    <td>React 18 · Vite · TypeScript · Tailwind · FastAPI · yt-dlp · FFmpeg · Docker · nginx · Vercel</td>
  </tr>
  <tr>
    <td valign="top"><b>focus</b></td>
    <td>Backend layout (extractors, downloader, routes, schemas kept separate) and concurrent batch jobs with live progress.</td>
  </tr>
  <tr>
    <td valign="top"><b>links</b></td>
    <td><a href="https://github.com/Hitesh754/Playlistkit">repository →</a> · <a href="https://playlistkit-hqup.vercel.app">live demo →</a><br><sub>The demo is the frontend; extraction needs the backend running.</sub></td>
  </tr>
</table>

### 03 · MediSphere

**A prototype health companion that turns medical paperwork into structured data.**

<table>
  <tr>
    <td width="110" valign="top"><b>problem</b></td>
    <td>Prescriptions and lab reports are hard to read and track. MediSphere scans a prescription, parses a lab report, schedules medication reminders and checks a logged meal against current medicines.</td>
  </tr>
  <tr>
    <td valign="top"><b>interesting</b></td>
    <td>Supabase Edge Functions wrap the AI calls (prescription scan, lab-report extraction, meal analysis, health summary). It also generates a patient-portfolio PDF and a QR code that shares a medication summary.</td>
  </tr>
  <tr>
    <td valign="top"><b>stack</b></td>
    <td>React 18 · TypeScript · Vite · Tailwind · shadcn/ui · Supabase Edge Functions · Gemini · jsPDF · Recharts</td>
  </tr>
  <tr>
    <td valign="top"><b>focus</b></td>
    <td>Structuring messy documents and keeping the client-side stores for medicines, adherence and notifications consistent.</td>
  </tr>
  <tr>
    <td valign="top"><b>scope</b></td>
    <td>Team prototype built with Kevin George. Not medical advice.</td>
  </tr>
  <tr>
    <td valign="top"><b>links</b></td>
    <td><a href="https://github.com/Hitesh754/Medisphere">repository →</a></td>
  </tr>
</table>

### 04 · RoadSense AI

**Road-damage detection with automated grievance ticketing.**

<table>
  <tr>
    <td width="110" valign="top"><b>problem</b></td>
    <td>Potholes and cracks cause crashes and water-logging, and municipal reporting is manual. This EPICS project detects damage in photos, video or live camera and turns detections into trackable tickets.</td>
  </tr>
  <tr>
    <td valign="top"><b>interesting</b></td>
    <td>A FastAPI inference backend (YOLOv8 + OpenCV) feeds a React app with geotagged tickets that move Reported → In Review → Scheduled → Repaired, plus a zone heatmap for admins.</td>
  </tr>
  <tr>
    <td valign="top"><b>stack</b></td>
    <td>React · TypeScript · Tailwind · FastAPI · YOLOv8 · OpenCV</td>
  </tr>
  <tr>
    <td valign="top"><b>scope</b></td>
    <td>Prototype, built by a six-person team under a faculty supervisor.</td>
  </tr>
  <tr>
    <td valign="top"><b>links</b></td>
    <td><a href="https://github.com/Hitesh754/Pothole-Vision-main">repository →</a></td>
  </tr>
</table>

<sub>Earlier work: Python data analysis ([sales](https://github.com/Hitesh754/Sales-data-anaysis), [Facebook data](https://github.com/Hitesh754/Facebook-data-analysis)), a [Streamlit movie recommender](https://github.com/Hitesh754/Movie-Recommendation), and a [Java campus records manager](https://github.com/Hitesh754/Camous-Course-and-Record-Management).</sub>

---

## ~/open-source

I want to get good at reading established codebases, improving docs and tooling, and shipping small fixes that maintainers can review. This is the full, current log of pull requests to other people's repositories.

| status | repository | pull request |
|:--|:--|:--|
| open | [ToolJet/ToolJet](https://github.com/ToolJet/ToolJet) | [#18365](https://github.com/ToolJet/ToolJet/pull/18365) · use the default border token for login fields |
| open | [swas02/3psLCCA-core-task](https://github.com/swas02/3psLCCA-core-task) | [#5](https://github.com/swas02/3psLCCA-core-task/pull/5) · LaTeX report generator |
| merged | [Ailurus98/Scroll_animate](https://github.com/Ailurus98/Scroll_animate) | [#1](https://github.com/Ailurus98/Scroll_animate/pull/1) · mobile vertical scrolling |
| merged ×12 | [TRUSTLAYERLABS-cyber-awareness](https://github.com/RAMINENI-TEJA-24MEI10040/TRUSTLAYERLABS-cyber-awareness) | team repo where I'm a collaborator: homepage, cyber-law module, language support, scanners |

<sub>Merged contributions to independent, maintainer-reviewed projects will be added here as they happen.</sub>

**Interests:** Linux desktop and shell tooling (Hyprland, Quickshell) · developer tools · maintainable code · documentation · learning from code review.

---

## ~/stack

```text
languages   Python · TypeScript / JavaScript · Bash · Java
web         React · Vite · Tailwind · FastAPI · Supabase
data / ML   pandas · NumPy · scikit-learn · Streamlit · OpenCV · YOLOv8 (RoadSense)
systems     Linux · Hyprland · Quickshell · Docker · nginx
```

---

## ~/activity

<p align="center">
  <a href="https://github.com/Hitesh754">
    <img src="https://ghchart.rshah.org/39d353/Hitesh754" alt="GitHub contribution graph for Hitesh754" width="100%">
  </a>
</p>

<sub>If the graph doesn't load, the same data is on the <a href="https://github.com/Hitesh754">profile page</a>.</sub>

---

## ~/contact

```text
github      github.com/Hitesh754
linkedin    linkedin.com/in/hitesh-choudhary-3133a1327
instagram   instagram.com/Hitesh231466
```

<p>
  <a href="https://github.com/Hitesh754">GitHub</a> ·
  <a href="https://www.linkedin.com/in/hitesh-choudhary-3133a1327">LinkedIn</a> ·
  <a href="https://www.instagram.com/Hitesh231466">Instagram</a>
</p>
