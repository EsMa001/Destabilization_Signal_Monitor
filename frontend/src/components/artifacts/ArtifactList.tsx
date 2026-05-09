import Link from "next/link";

import { StatusBadge } from "@/components/ui/StatusBadge";
import type { ArtifactRunGroup } from "@/types/api";

interface ArtifactListProps {
  runs: ArtifactRunGroup[];
  showRunLink?: boolean;
}

function formatDate(value?: string | null): string {
  if (!value) {
    return "n/a";
  }
  return new Date(value).toLocaleString("de-DE");
}

export function ArtifactList({ runs, showRunLink = true }: ArtifactListProps): React.JSX.Element {
  return (
    <div className="artifact-list" data-testid="artifact-list">
      {runs.map((run) => (
        <section key={run.run_id} className="artifact-run-panel">
          <p className="panel-title">Run {run.run_id}</p>
          <div className="artifact-run-header">
            <StatusBadge status={run.status} />
            <span className="muted">{formatDate(run.created_at)}</span>
            <span className="muted">{run.artifacts.length} artifacts</span>
            {run.bundle ? (
              <a href={run.bundle.path} className="linkish">
                Bundle
              </a>
            ) : (
              <span className="muted">No bundle</span>
            )}
            {showRunLink ? (
              <Link href={`/runs/${run.run_id}`} className="linkish">
                Run Detail
              </Link>
            ) : null}
          </div>

          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Name</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {run.artifacts.map((artifact) => (
                  <tr key={artifact.id}>
                    <td>{artifact.type}</td>
                    <td>{artifact.label}</td>
                    <td>
                      <StatusBadge
                        status={
                          artifact.available === false || artifact.status === "missing"
                            ? "error"
                            : artifact.status === "pending"
                              ? "warn"
                              : "ok"
                        }
                        label={artifact.status ?? (artifact.available === false ? "missing" : "available")}
                      />
                    </td>
                    <td>{formatDate(artifact.created_at)}</td>
                    <td>
                      {artifact.available === false ? (
                        <span className="muted">Unavailable</span>
                      ) : (
                        <a href={artifact.path} className="linkish">
                          Open
                        </a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ))}
    </div>
  );
}
