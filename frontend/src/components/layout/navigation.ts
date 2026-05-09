export interface NavItem {
  href: string;
  label: string;
  icon: string;
}

export const MAIN_NAV: NavItem[] = [
  { href: "/", label: "Overview", icon: "OV" },
  { href: "/runs", label: "Runs", icon: "RN" },
  { href: "/countries", label: "Countries", icon: "CT" },
  { href: "/compare", label: "Compare", icon: "CP" },
  { href: "/artifacts", label: "Artifacts", icon: "AR" },
  { href: "/coverage", label: "Coverage", icon: "CV" },
];

export const FOOTER_NAV: NavItem = {
  href: "/settings",
  label: "Settings",
  icon: "ST",
};
