<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/hero-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/hero-light.svg">
  <img alt="satriadhikara: software engineer at Grab, Geo / Mapping Platform" src="./assets/hero-dark.svg" width="100%">
</picture>

<br>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/satriadhikara/satriadhikara/output/neofetch-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/satriadhikara/satriadhikara/output/neofetch-light.svg">
  <img alt="neofetch-style card with role, stack and live GitHub stats" src="https://raw.githubusercontent.com/satriadhikara/satriadhikara/output/neofetch-dark.svg" width="100%">
</picture>

### `$ git log --author=me dbrepo`

<a href="https://github.com/DBRepo-Project/dbrepo"><b>DBRepo</b></a>: an open-source repository for research data stored in databases. <sub><code>java</code> <code>nginx</code> <code>helm</code> <code>docker</code></sub>

| pr | status | change |
|:--|:--|:--|
| [`#117`](https://github.com/DBRepo-Project/dbrepo/pull/117) | open | Stream table, view and subset exports straight from JDBC instead of staging them in S3, so exports are no longer capped by bucket space or heap. The gateway now streams over HTTP/1.1, so a failed export errors instead of arriving silently truncated. |
| [`#114`](https://github.com/DBRepo-Project/dbrepo/pull/114) | open | Dashboard moved to the official Grafana chart with pinned plugins, plus a CI check that keeps them pinned. |
| [`#113`](https://github.com/DBRepo-Project/dbrepo/pull/113) | merged | Java tests run against SeaweedFS after MinIO images disappeared from Docker Hub and broke CI. |
| [`#112`](https://github.com/DBRepo-Project/dbrepo/pull/112) | open | One-line installer fixed: the Compose distribution is now built, published to GitHub releases and installed from there. |
| [`#105`](https://github.com/DBRepo-Project/dbrepo/pull/105) | merged | Generated S3 and metrics credentials aligned in Docker Compose. |

### `$ ls ~/projects`

<table>
  <tr>
    <td width="50%" valign="top">
      <a href="https://github.com/satriadhikara/kolumba"><b>kolumba</b></a> <sub><code>typescript</code> <code>tanstack start</code></sub>
      <br><sub>Open-source webmail client for Stalwart Mail Server that speaks <b>JMAP</b> natively, with no IMAP translation layer. Batched method calls with result references create and submit an email in one request.</sub>
    </td>
    <td width="50%" valign="top">
      <a href="https://github.com/satriadhikara/jejak"><b>jejak</b></a> <sub>🏅 Gemastik 2025 finalist</sub>
      <br><sub>Pedestrian route and sidewalk-damage reporting app. Samples <b>Street View along your route</b> and has Gemini score the sidewalks, crossings and lighting. <code>expo</code> <code>hono</code></sub>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <a href="https://github.com/satriadhikara/dock"><b>dock</b></a> <sub>🥈 IFest 2025 Hackathon</sub>
      <br><sub>Contract lifecycle system for port logistics: a rich-text contract editor, draft-to-signing status flow and an AI contract assistant. <code>next.js</code> <code>hono</code> <code>fastapi</code></sub>
    </td>
    <td width="50%" valign="top">
      <a href="https://github.com/satriadhikara/babyblooms"><b>babyblooms</b></a> <sub>🏅 5th, Hack4Health IEEE ITB 2024</sub>
      <br><sub>Pregnancy companion that <b>links a mother's and partner's accounts</b> with a shared journal, community and trimester tracking. <code>expo</code> <code>hono</code></sub>
    </td>
  </tr>
</table>

### `$ ./pacman --eat contributions`

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/satriadhikara/satriadhikara/output/pacman-contribution-graph-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/satriadhikara/satriadhikara/output/pacman-contribution-graph.svg">
  <img alt="pacman eating my contribution graph" src="https://raw.githubusercontent.com/satriadhikara/satriadhikara/output/pacman-contribution-graph.svg">
</picture>

<p align="center">
  <a href="https://satriadhikara.com"><code>satriadhikara.com</code></a> ·
  <a href="mailto:hello@satriadhikara.com"><code>hello@satriadhikara.com</code></a> ·
  <a href="https://www.linkedin.com/in/satriadhikara"><code>linkedin</code></a>
  <br>
  <sub>banner and card are drawn by <a href="./scripts">zero-dependency python</a>; stats refresh daily via GitHub Actions</sub>
</p>
