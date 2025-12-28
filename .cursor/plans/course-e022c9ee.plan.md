<!-- e022c9ee-ad38-49a7-a1ce-8ec9dbb71e83 24c7fd14-f319-4cca-af92-bfebd5752fb3 -->
# Course Validator Frontend Plan

## Decisions

- Package manager: npm (keeps onboarding simple and matches Vite defaults)
- API mocking: add optional mock fallback toggle for `/api/ideas/analyze`

## Steps

1) Scaffold & deps

- Init Vite React TS in `frontend/`
- Install deps: axios, react-router-dom, tailwindcss + postcss/autoprefixer
- Configure Tailwind (`tailwind.config.js`, `postcss.config.js`, `src/index.css`)

2) Project wiring

- Add base files: `src/main.tsx`, `src/App.tsx`, router setup, layout shell
- Add `src/config.ts` with API base/env handling and mock toggle flag
- Add `src/context/AuthContext.tsx` stub with `isLoggedIn`, `login/logout`

3) Types

- Create `src/types/idea.ts` translating Pydantic models; keep score fields as string; optional nested types nullable

4) API layer

- Create `src/api/axiosClient.ts` using base URL + interceptors (optional)
- Create `src/api/ideaService.ts` with typed `analyzeIdea` POST and error normalization; include mock response helper when mock flag enabled

5) UI components

- `components/Header.tsx` consuming auth context with login/logout toggle and `/login` link placeholder
- Reusable UI bits: `AnalysisCard`, `Alert`, `Spinner`, `ScoreBoard` card trio, `SummaryCard`, `ScoreDetails` accordion, `JobMarketCard`, `YouTubeCard`
- Simple `NotFound` component for fallback route

6) Pages

- `pages/HomePage.tsx`: textarea input with validation, disabled Analyze until non-empty; loading state; error alert; renders cards grid on success; handles optional sections with "No data" messaging
- `pages/LoginPage.tsx` placeholder (for future flow)

7) Styling & UX polish

- Set up container, responsive grid, consistent score color thresholds (e.g., >=75 green, 50-74 amber, <50 red)
- Add typography and background styling via Tailwind utilities

8) Verification

- Run `npm run build` to ensure Vite/Tailwind wiring
- Manual test: toggle mock mode for UI sanity if backend unavailable; otherwise hit live `/api/ideas/analyze`

### To-dos

- [ ] Scaffold Vite TS app, install deps
- [ ] Wire router, layout, config, auth context
- [ ] Add idea request/response interfaces
- [ ] Implement axios client and ideaService with mock
- [ ] Build header and analysis UI components
- [ ] Implement Home/Login pages with states
- [ ] Polish styles and run npm run build