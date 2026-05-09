"use client";

import { useMemo, useRef, useState } from "react";

import { StateCard } from "@/components/ui/StateCard";
import type { CountryTrendPoint } from "@/types/api";

interface TrendSeries {
  id: string;
  label: string;
  color: string;
  points: CountryTrendPoint[];
}

interface TrendLineChartProps {
  series: TrendSeries[];
  height?: number;
}

interface ParsedPoint {
  x: number;
  y: number;
  value: number;
  timestamp: string;
}

function buildPath(points: Array<ParsedPoint | null>): string {
  let path = "";
  let started = false;
  for (const point of points) {
    if (!point) {
      started = false;
      continue;
    }
    if (!started) {
      path += `M ${point.x.toFixed(2)} ${point.y.toFixed(2)}`;
      started = true;
      continue;
    }
    path += ` L ${point.x.toFixed(2)} ${point.y.toFixed(2)}`;
  }
  return path;
}

export function TrendLineChart({ series, height = 220 }: TrendLineChartProps): React.JSX.Element {
  const svgRef = useRef<SVGSVGElement>(null);
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  const width = 760;
  const paddedHeight = height;
  const padding = { top: 20, right: 18, bottom: 28, left: 40 };
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = paddedHeight - padding.top - padding.bottom;

  const parsed = useMemo(() => {
    const maxLength = Math.max(0, ...series.map((entry) => entry.points.length));
    if (maxLength === 0) {
      return null;
    }

    const timeline = Array.from({ length: maxLength }, (_, index) => {
      for (const entry of series) {
        const timestamp = entry.points[index]?.timestamp;
        if (timestamp) {
          return timestamp;
        }
      }
      return "";
    });

    const values = series.flatMap((entry) => entry.points.map((point) => point.value).filter((value): value is number => value !== null));
    if (values.length === 0) {
      return null;
    }

    const min = Math.min(...values);
    const max = Math.max(...values);
    const span = max - min <= 0.0001 ? 1 : max - min;

    const parsedSeries = series.map((entry) => {
      const points: Array<ParsedPoint | null> = Array.from({ length: maxLength }, (_, index) => {
        const point = entry.points[index];
        if (!point || point.value === null) {
          return null;
        }
        const xRatio = maxLength <= 1 ? 0 : index / (maxLength - 1);
        const yRatio = (point.value - min) / span;
        return {
          x: padding.left + xRatio * innerWidth,
          y: padding.top + (1 - yRatio) * innerHeight,
          value: point.value,
          timestamp: point.timestamp,
        };
      });
      return {
        ...entry,
        points,
      };
    });

    return {
      min,
      max,
      maxLength,
      timeline,
      parsedSeries,
      firstLabel: timeline.find((label) => label.length > 0) ?? "",
      lastLabel: [...timeline].reverse().find((label) => label.length > 0) ?? "",
    };
  }, [series, innerHeight, innerWidth, padding.left, padding.top]);

  if (!parsed) {
    return <StateCard tone="empty" title="No trend data available" detail="Trend chart is waiting for country time-series data." />;
  }

  const safeHoverIndex =
    hoverIndex === null ? null : Math.max(0, Math.min(parsed.maxLength - 1, hoverIndex));
  const hoverX =
    safeHoverIndex === null
      ? null
      : padding.left + (parsed.maxLength <= 1 ? 0 : (safeHoverIndex / (parsed.maxLength - 1)) * innerWidth);
  const hoverTimestamp = safeHoverIndex !== null ? parsed.timeline[safeHoverIndex] : "";

  const yTicks = [0, 0.25, 0.5, 0.75, 1].map((ratio) => ({
    ratio,
    y: padding.top + (1 - ratio) * innerHeight,
    label: (parsed.min + ratio * (parsed.max - parsed.min)).toFixed(1),
  }));

  return (
    <div className="trend-chart-wrap">
      <svg
        ref={svgRef}
        className="trend-chart"
        viewBox={`0 0 ${width} ${paddedHeight}`}
        role="img"
        aria-label="Trend chart"
        onMouseMove={(event) => {
          if (!svgRef.current) {
            return;
          }
          const rect = svgRef.current.getBoundingClientRect();
          const cursorX = Math.max(0, Math.min(innerWidth, event.clientX - rect.left - padding.left));
          const ratio = innerWidth <= 0 ? 0 : cursorX / innerWidth;
          const nextIndex = parsed.maxLength <= 1 ? 0 : Math.round(ratio * (parsed.maxLength - 1));
          setHoverIndex(nextIndex);
        }}
        onMouseLeave={() => setHoverIndex(null)}
      >
        {yTicks.map((tick) => (
          <line
            key={tick.ratio}
            x1={padding.left}
            x2={width - padding.right}
            y1={tick.y}
            y2={tick.y}
            className="trend-grid-line"
          />
        ))}

        {yTicks.map((tick) => (
          <text key={`label_${tick.ratio}`} x={8} y={tick.y + 4} className="trend-axis-label">
            {tick.label}
          </text>
        ))}

        {hoverX !== null ? (
          <line
            x1={hoverX}
            x2={hoverX}
            y1={padding.top}
            y2={padding.top + innerHeight}
            className="trend-hover-line"
          />
        ) : null}

        {parsed.parsedSeries.map((entry) => (
          <g key={entry.id}>
            <path d={buildPath(entry.points)} style={{ stroke: entry.color }} className="trend-line" />
            {entry.points
              .filter((point): point is ParsedPoint => point !== null)
              .map((point) => (
                <circle key={`${entry.id}_${point.timestamp}`} cx={point.x} cy={point.y} r={2.2} style={{ fill: entry.color }} />
              ))}
          </g>
        ))}
      </svg>

      <div className="trend-chart-legend">
        {parsed.parsedSeries.map((entry) => (
          <span key={entry.id}>
            <span aria-hidden="true" style={{ background: entry.color }} />
            {entry.label}
          </span>
        ))}
      </div>

      {safeHoverIndex !== null ? (
        <div className="trend-hover-card">
          <p className="panel-title" style={{ marginBottom: "0.35rem" }}>
            {hoverTimestamp ? new Date(hoverTimestamp).toLocaleDateString("de-DE") : "No timestamp"}
          </p>
          <div className="trend-hover-grid">
            {parsed.parsedSeries.map((entry) => {
              const point = entry.points[safeHoverIndex];
              return (
                <div key={`hover_${entry.id}`} className="trend-hover-row">
                  <span>
                    <span aria-hidden="true" style={{ background: entry.color }} />
                    {entry.label}
                  </span>
                  <strong>{point ? point.value.toFixed(2) : "n/a"}</strong>
                </div>
              );
            })}
          </div>
        </div>
      ) : null}

      <div className="trend-axis-foot">
        <span>{parsed.firstLabel ? new Date(parsed.firstLabel).toLocaleDateString("de-DE") : "n/a"}</span>
        <span>{parsed.lastLabel ? new Date(parsed.lastLabel).toLocaleDateString("de-DE") : "n/a"}</span>
      </div>
    </div>
  );
}
