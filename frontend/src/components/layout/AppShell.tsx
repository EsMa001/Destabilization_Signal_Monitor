import type { PropsWithChildren } from "react";

import { SidebarNav } from "@/components/layout/SidebarNav";
import { TopBar } from "@/components/layout/TopBar";

export function AppShell({ children }: PropsWithChildren): React.JSX.Element {
  return (
    <div className="app-shell">
      <SidebarNav />

      <div className="workspace">
        <TopBar />
        <main className="workspace-main">{children}</main>
      </div>
    </div>
  );
}
