"use client";

import React, { useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Download, Image, FileSpreadsheet } from "lucide-react";
import { ChartData } from "@/lib/chart-types";
import { downloadCSV, downloadChartAsPNG, downloadChartAsSVG } from "@/lib/export-utils";

interface ExportButtonsProps {
  data: ChartData | null;
  chartRef?: React.RefObject<HTMLDivElement | null>;
}

export function ExportButtons({ data, chartRef }: ExportButtonsProps) {
  const handleDownloadCSV = () => {
    if (data) downloadCSV(data);
  };

  const handleDownloadPNG = () => {
    if (!chartRef?.current) return;
    const svg = chartRef.current.querySelector("svg");
    if (svg) downloadChartAsPNG(svg as SVGSVGElement);
  };

  const handleDownloadSVG = () => {
    if (!chartRef?.current) return;
    const svg = chartRef.current.querySelector("svg");
    if (svg) downloadChartAsSVG(svg as SVGSVGElement);
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-lg">Export</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <Button
          variant="outline"
          className="w-full justify-start"
          onClick={handleDownloadCSV}
          disabled={!data}
        >
          <FileSpreadsheet className="h-4 w-4 mr-2" />
          Download CSV
        </Button>
        <Button
          variant="outline"
          className="w-full justify-start"
          onClick={handleDownloadPNG}
          disabled={!data}
        >
          <Image className="h-4 w-4 mr-2" />
          Download PNG
        </Button>
        <Button
          variant="outline"
          className="w-full justify-start"
          onClick={handleDownloadSVG}
          disabled={!data}
        >
          <Download className="h-4 w-4 mr-2" />
          Download SVG
        </Button>
      </CardContent>
    </Card>
  );
}
