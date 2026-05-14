const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        AlignmentType, BorderStyle, WidthType, ShadingType, VerticalAlign } = require('docx');
const fs = require('fs');

const args = process.argv.slice(2);
const filmsJson = args[0];
const outputPath = args[1];

const films = JSON.parse(filmsJson);
const today = new Date().toLocaleDateString('uz-UZ', { day:'2-digit', month:'2-digit', year:'numeric' });
const totalParts = films.reduce((s, f) => s + f.parts_count, 0);

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

const headerShading = { fill: "1A3C5E", type: ShadingType.CLEAR };
const oddShading = { fill: "FFFFFF", type: ShadingType.CLEAR };
const evenShading = { fill: "EBF3FB", type: ShadingType.CLEAR };

// Column widths: №(700) + Nom(4500) + Kod(1500) + Qismlar(1560) = 8260
const COL = [700, 4500, 1500, 1560];

function cell(text, opts = {}) {
  return new TableCell({
    borders,
    width: { size: opts.width || 1000, type: WidthType.DXA },
    shading: opts.shading || oddShading,
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({
      alignment: opts.align || AlignmentType.LEFT,
      children: [new TextRun({
        text: String(text),
        bold: opts.bold || false,
        color: opts.color || "1A1A1A",
        font: "Arial",
        size: opts.size || 20,
      })]
    })]
  });
}

// Header row
const headerRow = new TableRow({
  tableHeader: true,
  children: [
    new TableCell({
      borders, width: { size: COL[0], type: WidthType.DXA },
      shading: headerShading, verticalAlign: VerticalAlign.CENTER,
      margins: { top: 100, bottom: 100, left: 120, right: 120 },
      children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "№", bold: true, color: "FFFFFF", font: "Arial", size: 20 })] })]
    }),
    new TableCell({
      borders, width: { size: COL[1], type: WidthType.DXA },
      shading: headerShading, verticalAlign: VerticalAlign.CENTER,
      margins: { top: 100, bottom: 100, left: 120, right: 120 },
      children: [new Paragraph({ alignment: AlignmentType.LEFT,
        children: [new TextRun({ text: "Kino nomi", bold: true, color: "FFFFFF", font: "Arial", size: 20 })] })]
    }),
    new TableCell({
      borders, width: { size: COL[2], type: WidthType.DXA },
      shading: headerShading, verticalAlign: VerticalAlign.CENTER,
      margins: { top: 100, bottom: 100, left: 120, right: 120 },
      children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Kod", bold: true, color: "FFFFFF", font: "Arial", size: 20 })] })]
    }),
    new TableCell({
      borders, width: { size: COL[3], type: WidthType.DXA },
      shading: headerShading, verticalAlign: VerticalAlign.CENTER,
      margins: { top: 100, bottom: 100, left: 120, right: 120 },
      children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Qismlar", bold: true, color: "FFFFFF", font: "Arial", size: 20 })] })]
    }),
  ]
});

const dataRows = films.map((film, i) => {
  const shading = i % 2 === 0 ? oddShading : evenShading;
  return new TableRow({
    children: [
      cell(i + 1, { width: COL[0], align: AlignmentType.CENTER, shading }),
      cell(film.name, { width: COL[1], bold: true, shading }),
      cell(film.code, { width: COL[2], align: AlignmentType.CENTER, color: "1A3C5E", shading }),
      cell(film.parts_count, { width: COL[3], align: AlignmentType.CENTER, shading }),
    ]
  });
});

// Footer row
const footerRow = new TableRow({
  children: [
    new TableCell({
      borders, columnSpan: 2,
      width: { size: COL[0] + COL[1], type: WidthType.DXA },
      shading: { fill: "F0F4F8", type: ShadingType.CLEAR },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({ alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: `Jami kinolar: ${films.length} ta`, bold: true, font: "Arial", size: 20, color: "1A3C5E" })] })]
    }),
    new TableCell({
      borders, columnSpan: 2,
      width: { size: COL[2] + COL[3], type: WidthType.DXA },
      shading: { fill: "F0F4F8", type: ShadingType.CLEAR },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: `Jami qismlar: ${totalParts} ta`, bold: true, font: "Arial", size: 20, color: "1A3C5E" })] })]
    }),
  ]
});

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } }
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 }
      }
    },
    children: [
      // Title
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 80 },
        children: [new TextRun({ text: "KINO VIBE BOT", bold: true, font: "Arial", size: 32, color: "1A3C5E" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 60 },
        children: [new TextRun({ text: "Kinolar ro'yxati", font: "Arial", size: 24, color: "555555" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 300 },
        border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "1A3C5E", space: 1 } },
        children: [
          new TextRun({ text: `Sana: ${today}`, font: "Arial", size: 18, color: "888888" }),
          new TextRun({ text: "     |     ", font: "Arial", size: 18, color: "CCCCCC" }),
          new TextRun({ text: `Jami: ${films.length} ta kino`, font: "Arial", size: 18, color: "888888" }),
        ]
      }),
      // Table
      new Table({
        width: { size: 8260, type: WidthType.DXA },
        columnWidths: COL,
        rows: [headerRow, ...dataRows, footerRow]
      }),
      // Footer note
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 240 },
        children: [new TextRun({ text: "@kino_vibe_bot tomonidan yaratildi", font: "Arial", size: 16, color: "AAAAAA", italics: true })]
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outputPath, buffer);
  console.log("OK");
});
