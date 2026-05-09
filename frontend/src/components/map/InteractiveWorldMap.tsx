"use client";

import { useMemo, useRef, useState } from "react";

import type { CountryAvailability } from "@/types/api";

interface InteractiveWorldMapProps {
  countries: CountryAvailability[];
  onCountrySelect: (countryCode: string) => void;
  selectedCountryCode?: string | null;
}

type GeoPoint = [number, number];

interface CountryGeometry {
  code: string;
  label: string;
  aliases?: string[];
  polygons: GeoPoint[][];
}

const VIEWBOX_WIDTH = 1000;
const VIEWBOX_HEIGHT = 460;
const MIN_LON = -180;
const MAX_LON = 180;
const MIN_LAT = -60;
const MAX_LAT = 85;

const COUNTRY_GEOMETRIES: CountryGeometry[] = [
  {
    code: "Germany",
    label: "Germany",
    aliases: ["DEU"],
    polygons: [[
      [5.8, 47.3], [7.5, 47.5], [8.3, 47.0], [9.5, 47.4], [10.6, 47.5], [12.0, 47.7], [12.7, 48.4], [13.8, 48.5],
      [14.7, 49.0], [14.9, 50.3], [14.4, 51.1], [14.7, 52.3], [14.1, 53.1], [12.8, 53.6], [11.2, 54.7], [9.5, 54.9],
      [8.4, 53.8], [7.1, 53.5], [6.0, 52.1], [6.1, 50.7], [5.8, 49.7], [6.0, 48.8], [5.8, 47.3],
    ]],
  },
  {
    code: "Israel",
    label: "Israel",
    aliases: ["ISR"],
    polygons: [[
      [34.26, 29.5], [34.55, 30.5], [34.66, 31.4], [34.73, 32.1], [34.98, 32.9], [35.5, 33.2], [35.64, 32.7],
      [35.58, 31.9], [35.53, 31.2], [35.45, 30.6], [35.42, 29.9], [35.35, 29.5], [34.8, 29.4], [34.26, 29.5],
    ]],
  },
  {
    code: "Iran",
    label: "Iran",
    aliases: ["IRN"],
    polygons: [[
      [44.0, 39.7], [46.2, 38.6], [48.0, 38.9], [50.2, 37.9], [52.2, 37.3], [54.8, 37.0], [56.8, 37.3], [59.0, 36.2],
      [61.0, 35.6], [63.2, 35.8], [63.1, 33.4], [61.4, 31.0], [60.7, 29.8], [61.0, 27.8], [59.2, 26.0], [57.8, 25.1],
      [55.4, 25.1], [53.2, 26.0], [51.3, 26.8], [49.7, 27.4], [48.4, 28.6], [46.3, 29.7], [45.1, 31.0], [44.2, 33.0],
      [44.1, 35.3], [44.0, 39.7],
    ]],
  },
  {
    code: "Ukraine",
    label: "Ukraine",
    aliases: ["UKR"],
    polygons: [[
      [22.1, 48.4], [23.8, 49.0], [24.6, 50.0], [26.1, 50.2], [28.2, 51.5], [30.3, 52.2], [32.2, 52.2], [34.0, 51.6],
      [35.9, 50.9], [37.6, 50.3], [39.9, 49.4], [39.5, 47.9], [38.4, 47.3], [36.7, 46.3], [35.2, 46.2], [33.6, 45.7],
      [31.9, 46.0], [30.5, 46.3], [29.2, 45.9], [27.6, 46.2], [26.2, 46.8], [24.7, 47.2], [23.1, 47.9], [22.1, 48.4],
    ]],
  },
  {
    code: "Russia",
    label: "Russia",
    aliases: ["RUS"],
    polygons: [[
      [27.0, 69.0], [40.0, 70.5], [55.0, 72.0], [75.0, 75.0], [100.0, 74.0], [125.0, 72.0], [150.0, 69.0], [170.0, 66.0],
      [178.0, 62.0], [170.0, 55.0], [160.0, 52.0], [150.0, 50.0], [140.0, 49.0], [130.0, 48.0], [120.0, 51.0], [110.0, 55.0],
      [100.0, 57.0], [90.0, 58.0], [80.0, 57.0], [70.0, 56.0], [60.0, 55.0], [50.0, 54.0], [42.0, 55.0], [36.0, 57.0],
      [30.0, 60.0], [27.0, 64.0], [27.0, 69.0],
    ]],
  },
  {
    code: "Japan",
    label: "Japan",
    aliases: ["JPN"],
    polygons: [
      [
        [141.0, 45.5], [145.5, 45.8], [146.1, 43.7], [144.8, 42.3], [142.5, 41.5], [140.7, 42.6], [141.0, 45.5],
      ],
      [
        [130.0, 33.0], [131.3, 34.3], [133.0, 34.6], [134.8, 35.2], [136.4, 36.0], [138.2, 37.2], [140.2, 38.6],
        [141.9, 40.2], [141.2, 41.2], [139.4, 40.8], [137.3, 39.4], [135.7, 37.9], [134.2, 36.4], [132.7, 35.5],
        [131.0, 34.2], [130.0, 33.0],
      ],
    ],
  },
  {
    code: "China",
    label: "China",
    aliases: ["CHN"],
    polygons: [[
      [73.5, 39.0], [76.0, 42.0], [80.2, 45.2], [87.0, 48.0], [94.5, 49.2], [102.0, 47.8], [110.0, 49.0], [118.0, 47.0],
      [124.0, 46.0], [132.0, 44.0], [134.8, 41.8], [131.5, 38.0], [127.0, 36.0], [122.0, 30.8], [120.0, 25.0], [113.0, 22.0],
      [108.0, 20.0], [103.0, 22.0], [99.0, 24.0], [95.0, 27.0], [91.0, 29.0], [87.0, 30.0], [82.0, 30.8], [78.0, 34.0],
      [74.0, 36.0], [73.5, 39.0],
    ]],
  },
  {
    code: "Taiwan",
    label: "Taiwan",
    aliases: ["TWN"],
    polygons: [[
      [120.0, 21.9], [121.0, 22.5], [121.5, 23.6], [121.4, 24.9], [121.0, 25.3], [120.4, 24.8], [120.1, 23.7], [120.0, 22.6],
      [120.0, 21.9],
    ]],
  },
  {
    code: "Poland",
    label: "Poland",
    aliases: ["POL"],
    polygons: [[
      [14.1, 49.0], [15.7, 49.2], [17.2, 50.0], [19.2, 49.0], [21.7, 49.4], [23.8, 50.2], [24.1, 51.8], [23.6, 53.8],
      [21.5, 54.3], [19.1, 54.8], [17.3, 54.2], [15.0, 53.8], [14.2, 52.4], [14.1, 49.0],
    ]],
  },
  {
    code: "Nigeria",
    label: "Nigeria",
    aliases: ["NGA"],
    polygons: [[
      [2.7, 6.3], [3.7, 7.2], [4.9, 8.5], [6.1, 10.2], [7.6, 11.0], [9.4, 12.4], [11.4, 13.4], [13.8, 13.9], [14.7, 12.2],
      [14.3, 10.3], [13.8, 8.5], [13.1, 7.2], [12.0, 6.0], [10.4, 6.0], [8.9, 4.7], [7.0, 4.3], [5.1, 5.0], [3.9, 5.4],
      [2.7, 6.3],
    ]],
  },
];

function normalizeKey(value: string): string {
  return value.trim().toLowerCase();
}

function projectPoint([lon, lat]: GeoPoint): { x: number; y: number } {
  const x = ((lon - MIN_LON) / (MAX_LON - MIN_LON)) * VIEWBOX_WIDTH;
  const y = ((MAX_LAT - lat) / (MAX_LAT - MIN_LAT)) * VIEWBOX_HEIGHT;
  return { x, y };
}

function polygonToPath(points: GeoPoint[]): string {
  if (points.length === 0) {
    return "";
  }
  const [first, ...rest] = points;
  const firstProjected = projectPoint(first);
  const commands = [`M${firstProjected.x.toFixed(2)} ${firstProjected.y.toFixed(2)}`];
  for (const point of rest) {
    const projected = projectPoint(point);
    commands.push(`L${projected.x.toFixed(2)} ${projected.y.toFixed(2)}`);
  }
  commands.push("Z");
  return commands.join(" ");
}

function getCountryStyle(entry?: CountryAvailability): { fill: string; stroke: string; strokeWidth: number } {
  if (!entry || !entry.has_data) {
    return {
      fill: "#1c2638",
      stroke: "#3a4458",
      strokeWidth: 1.0,
    };
  }
  if (entry.status === "active") {
    return {
      fill: "rgba(255, 180, 171, 0.45)",
      stroke: "#ffb4ab",
      strokeWidth: 1.7,
    };
  }
  if (entry.status === "watch") {
    return {
      fill: "rgba(246, 199, 122, 0.38)",
      stroke: "#f6c77a",
      strokeWidth: 1.7,
    };
  }
  return {
    fill: "rgba(81, 225, 165, 0.3)",
    stroke: "#51e1a5",
    strokeWidth: 1.7,
  };
}

export function InteractiveWorldMap({
  countries,
  onCountrySelect,
  selectedCountryCode = null,
}: InteractiveWorldMapProps): React.JSX.Element {
  const [hoveredCode, setHoveredCode] = useState<string | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState<{ x: number; y: number } | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const countryByKey = useMemo(() => {
    const map = new Map<string, CountryAvailability>();
    for (const entry of countries) {
      map.set(normalizeKey(entry.country_code), entry);
      map.set(normalizeKey(entry.country), entry);
    }
    return map;
  }, [countries]);

  const mappedCountryPaths = useMemo(() => {
    return COUNTRY_GEOMETRIES.map((geometry) => {
      const lookupKeys = [geometry.code, geometry.label, ...(geometry.aliases ?? [])];
      const record = lookupKeys.map((key) => countryByKey.get(normalizeKey(key))).find((entry) => entry !== undefined);
      return {
        geometry,
        record,
        path: geometry.polygons.map((polygon) => polygonToPath(polygon)).join(" "),
      };
    });
  }, [countryByKey]);

  const hoveredCountry = useMemo(() => {
    if (!hoveredCode) {
      return null;
    }
    const match = mappedCountryPaths.find((entry) => entry.geometry.code === hoveredCode);
    if (!match) {
      return null;
    }
    return {
      label: match.record?.country ?? match.geometry.label,
      record: match.record ?? null,
    };
  }, [hoveredCode, mappedCountryPaths]);

  const mappedKeys = useMemo(() => {
    const keys = new Set<string>();
    for (const geometry of COUNTRY_GEOMETRIES) {
      keys.add(normalizeKey(geometry.code));
      keys.add(normalizeKey(geometry.label));
      for (const alias of geometry.aliases ?? []) {
        keys.add(normalizeKey(alias));
      }
    }
    return keys;
  }, []);

  const unmappedCountries = useMemo(
    () => countries.filter((entry) => !mappedKeys.has(normalizeKey(entry.country_code)) && !mappedKeys.has(normalizeKey(entry.country))),
    [countries, mappedKeys],
  );

  const selectedKey = selectedCountryCode ? normalizeKey(selectedCountryCode) : null;

  return (
    <div className="world-map-wrap" ref={containerRef} data-testid="overview-map">
      <svg viewBox={`0 0 ${VIEWBOX_WIDTH} ${VIEWBOX_HEIGHT}`} className="world-map-svg" role="img" aria-label="World map by country availability">
        <rect x={0} y={0} width={VIEWBOX_WIDTH} height={VIEWBOX_HEIGHT} fill="#081022" />

        {[ -120, -60, 0, 60, 120 ].map((longitude) => {
          const projected = projectPoint([longitude, 0]);
          return (
            <line
              key={`lon_${longitude}`}
              x1={projected.x}
              y1={0}
              x2={projected.x}
              y2={VIEWBOX_HEIGHT}
              stroke="rgba(142, 208, 255, 0.08)"
              strokeWidth={1}
            />
          );
        })}

        {[ -30, 0, 30, 60 ].map((latitude) => {
          const projected = projectPoint([0, latitude]);
          return (
            <line
              key={`lat_${latitude}`}
              x1={0}
              y1={projected.y}
              x2={VIEWBOX_WIDTH}
              y2={projected.y}
              stroke="rgba(142, 208, 255, 0.08)"
              strokeWidth={1}
            />
          );
        })}

        {mappedCountryPaths.map(({ geometry, record, path }) => {
          const style = getCountryStyle(record);
          const isHovered = hoveredCode === geometry.code;
          const isSelected =
            selectedKey !== null &&
            (selectedKey === normalizeKey(geometry.code) || selectedKey === normalizeKey(geometry.label));
          return (
            <path
              key={geometry.code}
              d={path}
              fill={style.fill}
              stroke={style.stroke}
              strokeWidth={style.strokeWidth}
              className={`map-country ${isHovered || isSelected ? "hovered" : ""}`}
              onMouseEnter={() => setHoveredCode(geometry.code)}
              onMouseMove={(event) => {
                const rect = containerRef.current?.getBoundingClientRect();
                if (!rect) {
                  return;
                }
                setTooltipPosition({
                  x: event.clientX - rect.left + 12,
                  y: event.clientY - rect.top + 12,
                });
              }}
              onMouseLeave={() => {
                setHoveredCode(null);
                setTooltipPosition(null);
              }}
              onClick={() => onCountrySelect(record?.country_code ?? geometry.code)}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  onCountrySelect(record?.country_code ?? geometry.code);
                }
              }}
              role="button"
              tabIndex={0}
              aria-label={`${geometry.label} open detail`}
              data-testid={`map-country-${geometry.code.toLowerCase()}`}
            />
          );
        })}
      </svg>

      <div className="map-legend">
        <span>
          <span style={{ background: "rgba(255, 180, 171, 0.45)", borderColor: "#ffb4ab" }} />
          Active
        </span>
        <span>
          <span style={{ background: "rgba(246, 199, 122, 0.38)", borderColor: "#f6c77a" }} />
          Watch
        </span>
        <span>
          <span style={{ background: "rgba(81, 225, 165, 0.3)", borderColor: "#51e1a5" }} />
          Stable
        </span>
        <span>
          <span style={{ background: "#1c2638", borderColor: "#3a4458" }} />
          No data
        </span>
      </div>

      {unmappedCountries.length > 0 ? (
        <div className="map-unmapped">
          <p className="muted" style={{ margin: "0 0 0.35rem" }}>
            Countries without current geometry:
          </p>
          <div className="selection-grid">
            {unmappedCountries.map((country) => (
              <button
                key={country.country_code}
                type="button"
                className="btn"
                onClick={() => onCountrySelect(country.country_code)}
              >
                {country.country}
              </button>
            ))}
          </div>
        </div>
      ) : null}

      {hoveredCountry && tooltipPosition ? (
        <div className="map-tooltip" style={{ left: tooltipPosition.x, top: tooltipPosition.y }}>
          <strong>{hoveredCountry.label}</strong>
          <div className="map-tooltip-grid">
            <span>Score</span>
            <span>{hoveredCountry.record?.score?.toFixed(2) ?? "n/a"}</span>
            <span>Delta 7d</span>
            <span>
              {hoveredCountry.record?.delta_7d !== null && hoveredCountry.record?.delta_7d !== undefined
                ? `${hoveredCountry.record.delta_7d > 0 ? "+" : ""}${hoveredCountry.record.delta_7d.toFixed(2)}`
                : "n/a"}
            </span>
            <span>Freshness</span>
            <span>
              {hoveredCountry.record?.freshness_hours !== null && hoveredCountry.record?.freshness_hours !== undefined
                ? `${hoveredCountry.record.freshness_hours}h`
                : "n/a"}
            </span>
            <span>Coverage</span>
            <span>
              {hoveredCountry.record?.coverage_ratio !== null && hoveredCountry.record?.coverage_ratio !== undefined
                ? `${Math.round(hoveredCountry.record.coverage_ratio * 100)}%`
                : "n/a"}
            </span>
          </div>
        </div>
      ) : null}
    </div>
  );
}
