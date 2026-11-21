# Three-second hero loop

Original SkillLantern practice composition, 22 November 2026. Reuse and adapt
the original composition freely. Dependency licenses remain their own.

Requires Node.js/npm and a browser runtime. Open this folder in a terminal:

```sh
npm install
npm run studio
npm run render
npm run poster
```

`HeroLoop` is 1280 x 720, 30 fps, 90 frames (3 seconds), without audio or
external media. The renderer can download a browser on its first run.
`npm run render` writes `hero-loop.mp4`; `npm run poster` writes a frame-0 PNG.
The exact package versions record the example environment, not an evergreen
support promise. Review current Remotion license eligibility before use:
https://www.remotion.dev/docs/license/pricing

Agent skills are optional and separate from rendering this source:
https://www.remotion.dev/docs/ai/skills

No native agent installation or comparative skill performance is claimed.
