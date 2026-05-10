# Export-Artefakte

Dieses Verzeichnis enthaelt exportfaehige Fassungen der Projektdokumente.

## Enthaltene Formate

Fuer jedes Kern-Dokument wurden erzeugt:
- HTML
- DOCX
- PDF

## Dokumente

- `executive_summary_de.*`
- `scientific_paper.*`
- `scientific_paper_formal.*`
- `detailed_documentation.*`

## Hinweise

- Die HTML-Fassungen sind die vollstaendigsten exportorientierten Fassungen und referenzieren die SVG-Abbildungen direkt.
- Die DOCX- und PDF-Fassungen wurden automatisiert aus Markdown erzeugt.
- In DOCX/PDF werden SVG-Abbildungen in dieser Minimalfassung als referenzierte Abbildungshinweise gefuehrt, da in der aktuellen Umgebung keine robuste SVG-zu-Office/PDF-Einbettung verfuegbar war.
- Der Erzeugungsskript liegt in `build_exports.py`.
