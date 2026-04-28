import { ChartData } from "@/lib/chart-types";

export function downloadCSV(data: ChartData, filename?: string): void {
  if (!data.historical.length && !data.prediction.length) return;

  const rows: string[] = [];
  rows.push("Index,Value,Type");

  data.historical.forEach((point) => {
    rows.push(`${point.index},${point.value},historical`);
  });

  data.prediction.forEach((point) => {
    rows.push(`${point.index},${point.value},prediction`);
  });

  const csv = rows.join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = filename || "prediction_results.csv";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function downloadChartAsPNG(
  svgElement: SVGSVGElement | null,
  filename?: string
): void {
  if (!svgElement) return;

  const svgData = new XMLSerializer().serializeToString(svgElement);
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const rect = svgElement.getBoundingClientRect();
  canvas.width = rect.width * 2; // 2x for retina
  canvas.height = rect.height * 2;
  ctx.scale(2, 2);

  const img = new Image();
  img.onload = () => {
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, rect.width, rect.height);
    ctx.drawImage(img, 0, 0, rect.width, rect.height);

    const pngUrl = canvas.toDataURL("image/png");
    const link = document.createElement("a");
    link.href = pngUrl;
    link.download = filename || "chart.png";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  img.src =
    "data:image/svg+xml;base64," +
    btoa(unescape(encodeURIComponent(svgData)));
}

export function downloadChartAsSVG(
  svgElement: SVGSVGElement | null,
  filename?: string
): void {
  if (!svgElement) return;

  const svgData = new XMLSerializer().serializeToString(svgElement);
  const blob = new Blob([svgData], { type: "image/svg+xml" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = filename || "chart.svg";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
