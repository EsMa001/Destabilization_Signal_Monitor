import { Panel } from "@/components/ui/Panel";

export default function SettingsPage(): React.JSX.Element {
  return (
    <div className="page-grid">
      <div style={{ gridColumn: "span 8" }}>
        <Panel title="Settings">
          <p className="muted">
            MVP placeholder for frontend runtime settings (API base URL mode, fallback mode, analyst preferences).
          </p>
        </Panel>
      </div>
    </div>
  );
}
