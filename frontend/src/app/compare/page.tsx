import { Suspense } from "react";

import { StateCard } from "@/components/ui/StateCard";
import { CompareView } from "@/features/compare/CompareView";

export default function ComparePage(): React.JSX.Element {
  return (
    <Suspense
      fallback={
        <StateCard
          tone="loading"
          title="Loading compare workspace"
          detail="Preparing compare query context."
        />
      }
    >
      <CompareView />
    </Suspense>
  );
}
