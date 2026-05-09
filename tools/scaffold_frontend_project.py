from __future__ import annotations

import argparse
from pathlib import Path
from textwrap import dedent


FILES: dict[str, str] = {
    "frontend/README.md": dedent(
        """
        # Frontend

        Separates Web-Frontend für das Python-Analyseprojekt.

        ## Ziel
        - keine Fachlogik im Frontend
        - Kommunikation ausschließlich über die API
        - basiert auf Stitch-Design und Codex-Umsetzung

        ## Nächste Schritte
        1. `design/frontend_design_handoff.md` ausfüllen
        2. Codex mit Frontend-Anweisung auf dieses Verzeichnis ansetzen
        3. Frontend gegen API anbinden
        """
    ).strip()
    + "\n",
    "frontend/.gitignore": dedent(
        """
        node_modules/
        .next/
        dist/
        coverage/
        .env.local
        .env
        """
    ).strip()
    + "\n",
    "frontend/.env.example": dedent(
        """
        NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
        """
    ).strip()
    + "\n",
    "frontend/AGENTS.md": dedent(
        """
        # Frontend AGENTS

        ## Ziel
        Dieses Verzeichnis enthält ein separates Web-Frontend.
        Keine Fachlogik aus dem Python-Kern hier implementieren.

        ## Regeln
        - Frontend spricht nur mit der API.
        - Keine direkten Python-Imports.
        - Keine Kopplung an interne Backend-Dateipfade.
        - Fokus auf klare Komponentenstruktur, Typisierung und saubere Zustände.
        - Dark fullscreen analyst UI.
        """
    ).strip()
    + "\n",
    "frontend/design/frontend_design_handoff.md": dedent(
        """
        # Frontend Design Handoff

        ## 1. Ziel des Frontends
        TODO

        ## 2. Designquelle
        ### Stitch-Quelle
        - Stitch-Projektname:
        - Stitch-Link:
        - Version / Stand:
        - Datum:

        ### Exporte
        - Figma-Link:
        - HTML/CSS-Export-Pfad:
        - Screenshot-Ordner:

        ## 3. UX-/Designziel
        - cool
        - clean
        - dark
        - premium
        - fullscreen
        - analyst-focused

        ## 4. Globale Navigationsstruktur
        - Overview
        - Runs
        - Countries
        - Compare
        - Artifacts
        - Coverage
        - Settings

        ## 5. Seiteninventar
        ### Overview / Home
        TODO

        ### Run Builder
        TODO

        ### Run Monitor
        TODO

        ### Run Detail
        TODO

        ### Country Detail
        TODO

        ### Compare
        TODO

        ### Artifacts
        TODO

        ### Coverage / Data Status
        TODO

        ## 6. Designsystem-Regeln
        TODO

        ## 7. API-Kopplung
        TODO

        ## 8. Zustände
        TODO

        ## 9. Frontend-Komponenten-Kandidaten
        TODO

        ## 10. Nicht-Ziele
        - keine Fachlogik im Frontend
        - keine direkte Python-Kopplung
        - kein Desktop-only Ansatz

        ## 11. Offene Designentscheidungen
        TODO
        """
    ).strip()
    + "\n",
    "frontend/design/stitch_exports/.gitkeep": "",
    "frontend/design/stitch_exports/screenshots/.gitkeep": "",
    "frontend/design/stitch_exports/html_css_export/.gitkeep": "",
    "frontend/src/app/layout.tsx": dedent(
        """
        export default function RootLayout({
          children,
        }: Readonly<{ children: React.ReactNode }>) {
          return (
            <html lang="de">
              <body>{children}</body>
            </html>
          );
        }
        """
    ).strip()
    + "\n",
    "frontend/src/app/page.tsx": dedent(
        """
        export default function HomePage() {
          return <main>Overview placeholder</main>;
        }
        """
    ).strip()
    + "\n",
    "frontend/src/app/runs/page.tsx": dedent(
        """
        export default function RunsPage() {
          return <main>Run Monitor placeholder</main>;
        }
        """
    ).strip()
    + "\n",
    "frontend/src/app/runs/[runId]/page.tsx": dedent(
        """
        export default function RunDetailPage() {
          return <main>Run Detail placeholder</main>;
        }
        """
    ).strip()
    + "\n",
    "frontend/src/app/countries/[countryCode]/page.tsx": dedent(
        """
        export default function CountryDetailPage() {
          return <main>Country Detail placeholder</main>;
        }
        """
    ).strip()
    + "\n",
    "frontend/src/app/compare/page.tsx": dedent(
        """
        export default function ComparePage() {
          return <main>Compare placeholder</main>;
        }
        """
    ).strip()
    + "\n",
    "frontend/src/app/artifacts/page.tsx": dedent(
        """
        export default function ArtifactsPage() {
          return <main>Artifacts placeholder</main>;
        }
        """
    ).strip()
    + "\n",
    "frontend/src/app/coverage/page.tsx": dedent(
        """
        export default function CoveragePage() {
          return <main>Coverage placeholder</main>;
        }
        """
    ).strip()
    + "\n",
    "frontend/src/components/layout/.gitkeep": "",
    "frontend/src/components/map/.gitkeep": "",
    "frontend/src/components/runs/.gitkeep": "",
    "frontend/src/components/countries/.gitkeep": "",
    "frontend/src/components/artifacts/.gitkeep": "",
    "frontend/src/features/.gitkeep": "",
    "frontend/src/hooks/.gitkeep": "",
    "frontend/src/lib/api/client.ts": dedent(
        """
        const API_BASE_URL =
          process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

        export async function apiGet<T>(path: string): Promise<T> {
          const response = await fetch(`${API_BASE_URL}${path}`, {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            },
            cache: "no-store",
          });

          if (!response.ok) {
            throw new Error(`GET ${path} failed with status ${response.status}`);
          }

          return (await response.json()) as T;
        }

        export async function apiPost<TResponse, TRequest>(
          path: string,
          body: TRequest,
        ): Promise<TResponse> {
          const response = await fetch(`${API_BASE_URL}${path}`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(body),
          });

          if (!response.ok) {
            throw new Error(`POST ${path} failed with status ${response.status}`);
          }

          return (await response.json()) as TResponse;
        }
        """
    ).strip()
    + "\n",
    "frontend/src/types/api.ts": dedent(
        """
        export type RunStatus =
          | "queued"
          | "running"
          | "completed"
          | "failed"
          | "cancelled";

        export interface RunCreateRequest {
          name: string;
          countries: string[];
          window_days: number;
          config_overrides?: Record<string, unknown>;
        }

        export interface RunCreateResponse {
          run_id: string;
          status: RunStatus;
          created_at: string;
          links?: Record<string, string>;
        }

        export interface RunStatusResponse {
          run_id: string;
          status: RunStatus;
          created_at?: string;
          started_at?: string | null;
          finished_at?: string | null;
          progress?: {
            phase?: string;
            percent?: number;
            message?: string;
          };
          error?: {
            code?: string;
            message?: string;
          } | null;
        }
        """
    ).strip()
    + "\n",
    "frontend/src/styles/.gitkeep": "",
    "frontend/public/.gitkeep": "",
    "frontend/tests/.gitkeep": "",
    "frontend/package.json": dedent(
        """
        {
          "name": "security-analytics-frontend",
          "private": true,
          "version": "0.1.0",
          "scripts": {
            "dev": "next dev",
            "build": "next build",
            "start": "next start",
            "lint": "next lint",
            "typecheck": "tsc --noEmit"
          }
        }
        """
    ).strip()
    + "\n",
    "frontend/tsconfig.json": dedent(
        """
        {
          "compilerOptions": {
            "target": "ES2020",
            "lib": ["dom", "dom.iterable", "es2020"],
            "allowJs": false,
            "skipLibCheck": true,
            "strict": true,
            "noEmit": true,
            "esModuleInterop": true,
            "module": "esnext",
            "moduleResolution": "bundler",
            "resolveJsonModule": true,
            "isolatedModules": true,
            "jsx": "preserve",
            "incremental": true
          },
          "include": ["src/**/*.ts", "src/**/*.tsx"],
          "exclude": ["node_modules"]
        }
        """
    ).strip()
    + "\n",
}


def create_file(path: Path, content: str, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a separate frontend project structure."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root directory. Default: current directory.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files.",
    )
    args = parser.parse_args()

    root = args.root.resolve()

    for relative_path, content in FILES.items():
        create_file(root / relative_path, content, overwrite=args.overwrite)

    print("Frontend scaffold created under:", root / "frontend")
    print("Next steps:")
    print("1. Fill frontend/design/frontend_design_handoff.md")
    print("2. Export Stitch screens into frontend/design/stitch_exports/")
    print("3. Run Codex on the frontend/ directory using the prepared frontend instruction.")


if __name__ == "__main__":
    main()