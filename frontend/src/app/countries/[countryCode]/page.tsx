import { CountryDetailView } from "@/features/countries/CountryDetailView";

interface CountryDetailPageProps {
  params: Promise<{ countryCode: string }>;
}

export default async function CountryDetailPage({ params }: CountryDetailPageProps): Promise<React.JSX.Element> {
  const { countryCode } = await params;
  return <CountryDetailView countryCode={countryCode} />;
}
