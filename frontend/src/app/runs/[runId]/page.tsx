import { RunDetailView } from "@/features/runs/RunDetailView";

interface RunDetailPageProps {
  params: Promise<{ runId: string }>;
}

export default async function RunDetailPage({ params }: RunDetailPageProps): Promise<React.JSX.Element> {
  const { runId } = await params;
  return <RunDetailView runId={runId} />;
}
